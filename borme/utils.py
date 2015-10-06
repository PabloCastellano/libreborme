from .models import Company, Borme, Anuncio, Person, CargoCompany, CargoPerson, BormeLog
from mongoengine.errors import ValidationError, NotUniqueError

from django.conf import settings
from django.utils.text import slugify
import datetime

import bormeparser
from bormeparser.borme import BormeXML
from bormeparser.exceptions import BormeDoesntExistException
from bormeparser.regex import is_company, is_acto_cargo_entrante
from bormeparser.utils import FIRST_BORME

import calendar
import time
import os

# FIXME:
#settings.BORME_DIR
# descarga -> parse -> import -> mueve a carpeta archive
# Problema: download_pdfs va a bajar de nuevo los archivos en tmp si ya estan procesados

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def _import1(borme):
    """
    borme: bormeparser.Borme
    """
    logger.info('\nBORME CVE: %s (%s)' % (borme.cve, borme.provincia))
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    borme_log, created = BormeLog.objects.get_or_create(borme_cve=borme.cve)
    if created:
        borme_log.date_created = datetime.datetime.now()
        borme_log.date_updated = borme_log.date_created
        borme_log.path = borme.filename
        borme_log.save()
    else:
        borme_log.date_updated = datetime.datetime.now()
        borme_log.save()
        if borme_log.parsed:
            logger.warn('%s ya ha sido analizado.' % borme.cve)
            return results

    nuevo_borme, created = Borme.objects.get_or_create(cve=borme.cve)
    if created:
        logger.debug('Creando borme %s' % borme.cve)
        results['created_bormes'] += 1
        nuevo_borme.date = borme.date
        nuevo_borme.url = borme.url
        nuevo_borme.from_reg = borme.anuncios_rango[0]
        nuevo_borme.until_reg = borme.anuncios_rango[1]
        nuevo_borme.province = borme.provincia.name
        nuevo_borme.section = borme.seccion
        #year, type, from_page, until_page, pages
        # num?, filename?

    # TODO: borrar si hubieran actos para este borme?
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.debug('%d: Importando anuncio: %s' % (n, anuncio))
            try:
                company, created = Company.objects.get_or_create(name=anuncio.empresa)
                if created:
                    logger.debug('Creando empresa %s' % anuncio.empresa)
                    results['created_companies'] += 1
                company.in_bormes.append(nuevo_borme)
            except NotUniqueError as e:
                slug_c = slugify(anuncio.empresa)
                company = Company.objects.get(slug=slug_c)
                logger.warn('WARNING: Empresa similar. Mismo slug: %s' % slug_c)
                logger.warn('%s\n%s\n' % (company.name, anuncio.empresa))
                results['errors'] += 1

            nuevo_anuncio, created = Anuncio.objects.get_or_create(id_anuncio=anuncio.id)
            if created:
                logger.debug('Creando anuncio %d: %s' % (anuncio.id, anuncio.empresa))
                results['created_anuncios'] += 1
                nuevo_anuncio.borme = nuevo_borme
                nuevo_anuncio.company = company
                nuevo_anuncio.datos_registrales = anuncio.datos_registrales

            for acto in anuncio.get_borme_actos():
                logger.debug(acto.name)
                logger.debug(acto.value)
                if isinstance(acto, bormeparser.borme.BormeActoCargo):
                    for nombre_cargo, nombres in acto.cargos.items():
                        logger.debug('%s %s %d' % (nombre_cargo, nombres, len(nombres)))
                        lista_cargos = []
                        for nombre in nombres:
                            logger.debug('  %s' % nombre)
                            if is_company(nombre):
                                try:
                                    c, created = Company.objects.get_or_create(name=nombre)
                                    if created:
                                        logger.debug('Creando empresa: %s' % nombre)
                                        results['created_companies'] += 1

                                except NotUniqueError as e:
                                    slug_c = slugify(nombre)
                                    c = Company.objects.get(slug=slug_c)
                                    logger.warn('WARNING: Empresa similar. Mismo slug: %s' % slug_c)
                                    logger.warn('%s\n%s\n' % (c.name, nombre))
                                    results['errors'] += 1

                                c.anuncios.append(nuevo_anuncio)
                                c.in_bormes.append(nuevo_borme)
                                cargo = CargoCompany(title=nombre_cargo, name=c)
                                if is_acto_cargo_entrante(acto.name):
                                    cargo.date_from = borme.date
                                    cargo_embed = CargoCompany(title=nombre_cargo, name=company, date_from=borme.date)
                                    c.update_cargos_entrantes([cargo_embed])
                                else:
                                     cargo.date_to = borme.date
                                     cargo_embed = CargoCompany(title=nombre_cargo, name=company, date_to=borme.date)
                                     c.update_cargos_salientes([cargo_embed])
                                c.save()
                            else:
                                try:
                                    p, created = Person.objects.get_or_create(name=nombre)
                                    if created:
                                        logger.debug('Creando persona: %s' % nombre)
                                        results['created_persons'] += 1

                                except NotUniqueError as e:
                                    slug_p = slugify(nombre)
                                    p = Person.objects.get(slug=slug_p)
                                    logger.warn('WARNING: Persona similar. Mismo slug: %s' % slug_p)
                                    logger.warn('%s\n%s\n' % (p.name, nombre))
                                    results['errors'] += 1

                                p.in_companies.append(company)
                                p.in_bormes.append(nuevo_borme)
                                cargo = CargoPerson(title=nombre_cargo, name=p)
                                if is_acto_cargo_entrante(acto.name):
                                    cargo.date_from = borme.date
                                    cargo_embed = CargoCompany(title=nombre_cargo, name=company, date_from=borme.date)
                                    p.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo.date_to = borme.date
                                    cargo_embed = CargoCompany(title=nombre_cargo, name=company, date_to=borme.date)
                                    p.update_cargos_salientes([cargo_embed])
                                p.save()

                            lista_cargos.append(cargo)

                        kk = acto.name.replace('.', '||')
                        nuevo_anuncio.actos[kk] = lista_cargos

                    if is_acto_cargo_entrante(acto.name):
                        company.update_cargos_entrantes(lista_cargos)
                    else:
                        company.update_cargos_salientes(lista_cargos)
                else:
                    # FIXME:
                    # mongoengine.errors.ValidationError: ValidationError (Anuncio:55b37c97cf28dd2cfa8d069e) (Invalid diction
                    # ary key name - keys may not contain "." or "$" characters: ['actos'])
                    kk = acto.name.replace('.', '||')
                    nuevo_anuncio.actos[kk] = acto.value

            nuevo_anuncio.save()
            company.anuncios.append(nuevo_anuncio)
            company.save()
            nuevo_borme.anuncios.append(nuevo_anuncio)
            nuevo_borme.save()
            nuevo_borme = Borme.objects.get(cve=borme.cve)  # Trick to avoid excessive memory consuming in large PDFs

        except ValidationError as e:
            logger.error('ERROR importing borme')
            logger.error(e)
            results['errors'] += 1

    nuevo_borme.save()

    borme_log.errors = results['errors']
    borme_log.parsed = True
    borme_log.date_parsed = datetime.datetime.now()
    borme_log.save()
    return results


def get_borme_pdf_path(date):
    year = '%02d' % date.year
    month = '%02d' % date.month
    day = '%02d' % date.day
    return os.path.join(settings.BORME_PDF_ROOT, year, month, day)


def import_borme_download(date, seccion=bormeparser.SECCION.A, download=True):
    """
    date: "2015", "2015-01", "2015-01-30", "--init"
    """
    if date == '--init':
        begin = FIRST_BORME
        end = datetime.date.today()
    else:
        date = tuple(map(int, date.split('-')))  # TODO: exception

        if len(date) == 3:  # 2015-06-02
            begin = datetime.date(*date)
            try:
                _import_borme_download_range2(begin, begin, seccion, download)
            except BormeDoesntExistException:
                logger.info('It looks like there is no BORME for this date. Nothing was downloaded')
            return
        elif len(date) == 2:  # 2015-06
            _, lastday = calendar.monthrange(*date)
            begin = datetime.date(date[0], date[1], 1)
            end = datetime.date(date[0], date[1], lastday)

        elif len(date) == 1:  # 2015
            begin = datetime.date(date[0], 1, 1)
            end = datetime.date(date[0], 12, 31)

    try:
        _import_borme_download_range2(begin, end, seccion, download)
    except BormeDoesntExistException:
        try:
            begin = begin + datetime.timedelta(days=1)
            _import_borme_download_range2(begin, end, seccion, download)
        except BormeDoesntExistException:
            begin = begin + datetime.timedelta(days=1)
            _import_borme_download_range2(begin, end, seccion, download)


def _import_borme_download_range2(begin, end, seccion, download, strict=False):
    """
    strict: Para en caso de error grave
    """
    next_date = begin
    total_results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}
    total_start_time = time.time()

    while next_date and next_date <= end:
        bxml = BormeXML.from_date(next_date)
        # TODO: BormeDoesntExist?

        # Add FileHandlers
        # TODO: Renombrar .1, .2, .3...
        logpath = os.path.join(settings.BORME_LOG_ROOT, 'imports', '%02d-%02d' % (bxml.date.year, bxml.date.month))
        os.makedirs(logpath, exist_ok=True)

        fh1_path = os.path.join(logpath, '%02d_info.txt' % bxml.date.day)
        fh1 = logging.FileHandler(fh1_path)
        fh1.setLevel(logging.INFO)
        logger.addHandler(fh1)

        fh2_path = os.path.join(logpath, '%02d_error.txt' % bxml.date.day)
        fh2 = logging.FileHandler(fh2_path)
        fh2.setLevel(logging.WARNING)
        logger.addHandler(fh2)

        pdf_path = get_borme_pdf_path(bxml.date)
        os.makedirs(pdf_path, exist_ok=True)
        logger.info('============================================================')
        logger.info('Ran import_borme_download at %s' % datetime.datetime.now())
        logger.info('  Import date: %s. Section: %s' % (bxml.date.isoformat(), seccion))
        logger.info('============================================================')
        logger.info(pdf_path)

        print('\nPATH: %s\nDATE: %s\nSECCION: %s\n' % (pdf_path, bxml.date, seccion))

        bormes = []
        if download:
            _, files = bxml.download_pdfs(pdf_path, seccion=seccion)
        else:
            _, _, files = next(os.walk(pdf_path))
            files = list(map(lambda x: os.path.join(pdf_path, x), files))

        for filepath in files:
            if filepath.endswith('-99.pdf'):
                continue
            logger.info('%s' % filepath)
            try:
                bormes.append(bormeparser.parse(filepath))
            except Exception as e:
                logger.error('[X] Error grave en bormeparser.parse(): %s' % filepath)
                logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                if strict:
                    logger.error('[X] Una vez arreglado, reanuda la importación:')
                    logger.error('[X]   python manage.py importbormetoday local')
                    return False, total_results

        for borme in sorted(bormes):
            start_time = time.time()
            try:
                results = _import1(borme)
            except Exception as e:
                logger.error('[%s] Error grave en _import1:' % borme.cve)
                logger.error('[%s] %s' % (borme.cve, e))
                logger.error('[%s] Prueba importar manualmente en modo detallado para ver el error:' % borme.cve)
                logger.error('[%s]   python manage.py importbormefile %s -v 3' % (borme.cve, borme.filename))
                if strict:
                    logger.error('[%s] Una vez arreglado, reanuda la importación:' % borme.cve)
                    logger.error('[%s]   python manage.py importbormetoday local' % borme.cve)
                    return False, total_results

            total_results['created_anuncios'] += results['created_anuncios']
            total_results['created_bormes'] += results['created_bormes']
            total_results['created_companies'] += results['created_companies']
            total_results['created_persons'] += results['created_persons']
            total_results['errors'] += results['errors']

            if not all(map(lambda x: x== 0, total_results.values())):
                print_results(results, borme)
                elapsed_time = time.time() - start_time
                logger.info('[%s] Elapsed time: %.2f seconds' % (borme.cve, elapsed_time))

        # Remove handlers
        logger.removeHandler(fh1)
        logger.removeHandler(fh2)
        next_date = bxml.next_borme

    elapsed_time = time.time() - total_start_time
    logger.info('\nBORMEs creados: %d' % total_results['created_bormes'])
    logger.info('Anuncios creados: %d' % total_results['created_anuncios'])
    logger.info('Empresas creadas: %d' % total_results['created_companies'])
    logger.info('Personas creadas: %d' % total_results['created_persons'])
    logger.info('Total elapsed time: %.2f seconds' % elapsed_time)

    return True, total_results


def import_borme_file(filename):
    """
    Import BORME to MongoDB database

    :param filename:
    :return:
    """
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    try:
        borme = bormeparser.parse(filename)
        results = _import1(borme)
    except Exception as e:
        logger.error('[X] Error grave en bormeparser.parse(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if not all(map(lambda x: x== 0, results.values())):
        print_results(results, borme)
    return True, results


def print_results(results, borme):
    logger.info('[%s] BORMEs creados: %d' % (borme.cve, results['created_bormes']))
    logger.info('[%s] Anuncios creados: %d/%d' % (borme.cve, results['created_anuncios'], len(borme.get_anuncios())))
    logger.info('[%s] Empresas creadas: %d' % (borme.cve, results['created_companies']))
    logger.info('[%s] Personas creadas: %d' % (borme.cve, results['created_persons']))
