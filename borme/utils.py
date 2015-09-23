from .models import Company, Borme, Anuncio, Person, CargoCompany, CargoPerson, BormeLog
from mongoengine.errors import ValidationError, NotUniqueError

from django.conf import settings
from django.utils.text import slugify
from bormeparser.regex import is_company, is_acto_cargo_entrante
from datetime import datetime

import bormeparser
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
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

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

    # TODO: Don't parse if borme_log.parsed
    borme_log, created = BormeLog.objects.get_or_create(borme_cve=borme.cve)
    if created:
        borme_log.date_created = datetime.now()
        borme_log.date_updated = borme_log.date_created
    else:
        borme_log.date_updated = datetime.now()
    borme_log.path = borme.filename
    borme_log.save()

    # TODO: borrar si hubieran actos para este borme?
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.debug('%d: Importando anuncio: %s' % (n, anuncio))
            # TODO: Buscar por slug
            try:
                company, created = Company.objects.get_or_create(name=anuncio.empresa)
                if created:
                    logger.debug('Creando empresa %s' % anuncio.empresa)
                    results['created_companies'] += 1
                company.in_bormes.append(nuevo_borme)
            except NotUniqueError as e:
                logger.error('ERROR creando empresa: %s' % anuncio.empresa)
                logger.error(e)
                results['errors'] += 1
                continue

            nuevo_anuncio, created = Anuncio.objects.get_or_create(borme=nuevo_borme, id_anuncio=anuncio.id, company=company)
            if created:
                logger.debug('Creando anuncio %d: %s' % (anuncio.id, anuncio.empresa))
                results['created_anuncios'] += 1

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
                                except NotUniqueError as e:
                                    logger.error('ERROR creando empresa: %s' % nombre)
                                    logger.error(e)
                                    results['errors'] += 1

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

        except ValidationError as e:
            logger.error('ERROR importing borme')
            logger.error(e)
            results['errors'] += 1

        nuevo_borme.save()

    borme_log.errors = results['errors']
    if results['errors'] == 0:
        borme_log.parsed = True
        borme_log.date_parsed = datetime.now()
    borme_log.save()
    return results


def get_borme_pdf_path(date):
    year = '%02d' % date.year
    month = '%02d' % date.month
    day = '%02d' % date.day
    return os.path.join(settings.BORME_PDF_ROOT, year, month, day)


def import_borme_download(date, seccion=bormeparser.SECCION.A, download=True):
    """
    Download and import BORME to MongoDB database

    :param filename:
    :return:
    """

    if isinstance(date, tuple):
        date = datetime.date(year=date[0], month=date[1], day=date[2])

    # Add FileHandlers
    # TODO: Renombrar .1, .2, .3...
    logpath = os.path.join(settings.BORME_LOG_ROOT, 'imports', '%02d-%02d' % (date.year, date.month))
    os.makedirs(logpath, exist_ok=True)

    fh1_path = os.path.join(logpath, '%02d_info.txt' % date.day)
    fh1 = logging.FileHandler(fh1_path)
    fh1.setLevel(logging.INFO)
    logger.addHandler(fh1)

    fh2_path = os.path.join(logpath, '%02d_error.txt' % date.day)
    fh2 = logging.FileHandler(fh2_path)
    fh2.setLevel(logging.WARNING)
    logger.addHandler(fh2)

    new_path = get_borme_pdf_path(date)
    os.makedirs(new_path, exist_ok=True)
    logger.info('============================================================')
    logger.info('Ran import_borme_download at %s' % datetime.now())
    logger.info('  Import date: %s. Section: %s' % (date.isoformat(), seccion))
    logger.info('============================================================')
    logger.info(new_path)

    bormes = []
    if download:
        _, files = bormeparser.download_pdfs(date, new_path, seccion=seccion)
    else:
        _, _, files = next(os.walk(new_path))
        files = list(map(lambda x: os.path.join(new_path, x), files))

    for filepath in files:
        if filepath.endswith('-99.pdf'):
            continue
        logger.info('%s' % filepath)
        bormes.append(bormeparser.parse(filepath))

    total_results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}
    for borme in sorted(bormes):
        results = _import1(borme)
        total_results['created_anuncios'] += results['created_anuncios']
        total_results['created_bormes'] += results['created_bormes']
        total_results['created_companies'] += results['created_companies']
        total_results['created_persons'] += results['created_persons']
        total_results['errors'] += results['errors']
        print_results(results, borme)

    logger.info('\nBORMEs creados: %d' % total_results['created_bormes'])
    logger.info('Anuncios creados: %d' % total_results['created_anuncios'])
    logger.info('Empresas creadas: %d' % total_results['created_companies'])
    logger.info('Personas creadas: %d' % total_results['created_persons'])

    # Remove handlers
    logger.removeHandler(fh1)
    logger.removeHandler(fh2)


def import_borme_file(filename):
    """
    Import BORME to MongoDB database

    :param filename:
    :return:
    """
    borme = bormeparser.parse(filename)
    results = _import1(borme)

    print_results(results, borme)


def print_results(results, borme):
    logger.info('\nBORME CVE: %s' % borme.cve)
    logger.info('BORMEs creados: %d' % results['created_bormes'])
    logger.info('Anuncios creados: %d/%d' % (results['created_anuncios'], len(borme.get_anuncios())))
    logger.info('Empresas creadas: %d' % results['created_companies'])
    logger.info('Personas creadas: %d' % results['created_persons'])
    return True
