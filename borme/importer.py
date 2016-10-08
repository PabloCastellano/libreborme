from .models import Company, Borme, Anuncio, Person, BormeLog

from django.conf import settings
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone

from borme.utils import get_file

import bormeparser
from bormeparser.borme import BormeXML
from bormeparser.exceptions import BormeDoesntExistException
from bormeparser.regex import is_company, is_acto_cargo_entrante, regex_empresa_tipo
from bormeparser.utils import FIRST_BORME

import datetime
import logging
import time
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


@transaction.atomic
def _import1(borme, fetch_url=False):
    """
    borme: bormeparser.Borme
    fetch_url: Si la instancia borme no contiene la URL, obtenerla de todas formas (necesita conexión a Internet)
    """
    logger.info('\n[{cve}] ({date}, {provincia}, [{rango[0]}-{rango[1]}])'.format(cve=borme.cve, date=borme.date, provincia=borme.provincia, rango=borme.anuncios_rango))
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0,
               'total_companies': 0, 'total_persons': 0, 'errors': 0}

    try:
        nuevo_borme = Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        if borme._url or fetch_url:
            borme_url = borme.url
        else:
            borme_url = None
        nuevo_borme = Borme(cve=borme.cve, date=borme.date, url=borme_url, from_reg=borme.anuncios_rango[0],
                            until_reg=borme.anuncios_rango[1], province=borme.provincia.name, section=borme.seccion)
        #year, type, from_page, until_page, pages
        # num?, filename?
        logger.debug('Creando borme %s' % borme.cve)
        nuevo_borme.save()
        results['created_bormes'] += 1

    try:
        borme_log = BormeLog.objects.get(borme=nuevo_borme)
    except BormeLog.DoesNotExist:
        borme_log = BormeLog(borme=nuevo_borme, path=borme.filename)

    if borme_log.parsed:
        logger.warn('%s ya ha sido analizado.' % borme.cve)
        return results

    borme_log.save()  # date_updated

    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.debug('%d: Importando anuncio: %s' % (n, anuncio))
            results['total_companies'] += 1
            empresa, tipo = regex_empresa_tipo(anuncio.empresa)
            if tipo == '':
                logger.warn('[%s]: Tipo de empresa no detectado: %s' % (borme.cve, empresa))
            slug_c = slugify(empresa)
            try:
                company = Company.objects.get(slug=slug_c)
                if company.name != empresa:
                    logger.warn('[%s] WARNING: Empresa similar. Mismo slug: %s' % (borme.cve, slug_c))
                    logger.warn('[%s] %s\n[%s] %s\n' % (borme.cve, company.name, borme.cve, empresa, tipo))
                    results['errors'] += 1
            except Company.DoesNotExist:
                company = Company(name=empresa, type=tipo)
                company.generate_slug()
                logger.debug('Creando empresa %s %s' % (empresa, tipo))
                results['created_companies'] += 1

            try:
                nuevo_anuncio = Anuncio.objects.get(id_anuncio=anuncio.id, year=borme.date.year)
            except Anuncio.DoesNotExist:
                nuevo_anuncio = Anuncio(id_anuncio=anuncio.id, year=borme.date.year, borme=nuevo_borme,
                                        datos_registrales=anuncio.datos_registrales, registro=anuncio.registro)
                logger.debug('Creando anuncio %d: %s %s' % (anuncio.id, empresa, tipo))
                results['created_anuncios'] += 1

            borme_embed = {'cve': nuevo_borme.cve, 'url': nuevo_borme.url, 'num': nuevo_anuncio.id_anuncio, 'year': nuevo_anuncio.year}
            company.add_in_bormes(borme_embed)

            for acto in anuncio.get_borme_actos():
                logger.debug(acto.name)
                logger.debug(acto.value)
                if isinstance(acto, bormeparser.borme.BormeActoCargo):
                    lista_cargos = []
                    for nombre_cargo, nombres in acto.cargos.items():
                        logger.debug('%s %s %d' % (nombre_cargo, nombres, len(nombres)))
                        for nombre in nombres:
                            logger.debug('  %s' % nombre)
                            if is_company(nombre):
                                results['total_companies'] += 1
                                empresa, tipo = regex_empresa_tipo(nombre)
                                slug_c = slugify(empresa)
                                try:
                                    c = Company.objects.get(slug=slug_c)
                                    if c.name != empresa:
                                        logger.warn('[%s] WARNING: Empresa similar 2. Mismo slug: %s' % (borme.cve, slug_c))
                                        logger.warn('[%s] %s\n[%s] %s %s\n' % (borme.cve, c.name, borme.cve, empresa, tipo))
                                        results['errors'] += 1
                                except Company.DoesNotExist:
                                    c = Company(name=empresa, type=tipo)
                                    c.generate_slug()
                                    logger.debug('Creando empresa: %s %s' % (empresa, tipo))
                                    results['created_companies'] += 1

                                c.anuncios.append({'id': nuevo_anuncio.id_anuncio, 'year': nuevo_anuncio.year})
                                c.add_in_bormes(borme_embed)

                                cargo = {'title': nombre_cargo, 'name': c.fullname, 'slug': c.slug, 'type': 'company'}
                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'slug': company.slug, 'date_from': borme.date.isoformat(), 'type': 'company'}
                                    c.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'slug': company.slug, 'date_to': borme.date.isoformat(), 'type': 'company'}
                                    c.update_cargos_salientes([cargo_embed])
                                c.date_updated = borme.date
                                c.save()
                            else:
                                results['total_persons'] += 1
                                slug_p = slugify(nombre)
                                try:
                                    p = Person.objects.get(slug=slug_p)
                                    if p.name != nombre:
                                        logger.warn('[%s] WARNING: Persona similar. Mismo slug: %s' % (borme.cve, slug_p))
                                        logger.warn('[%s] %s\n[%s] %s\n' % (borme.cve, p.name, borme.cve, nombre))
                                        results['errors'] += 1
                                except Person.DoesNotExist:
                                    p = Person(name=nombre)
                                    p.generate_slug()
                                    logger.debug('Creando persona: %s' % nombre)
                                    results['created_persons'] += 1

                                p.add_in_companies(company.fullname)
                                p.add_in_bormes(borme_embed)

                                cargo = {'title': nombre_cargo, 'name': p.name, 'slug': p.slug, 'type': 'person'}
                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'slug': company.slug, 'date_from': borme.date.isoformat()}
                                    p.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'slug': company.slug, 'date_to': borme.date.isoformat()}
                                    p.update_cargos_salientes([cargo_embed])

                                p.date_updated = borme.date
                                p.save()
                            lista_cargos.append(cargo)

                    nuevo_anuncio.actos[acto.name] = lista_cargos

                    if is_acto_cargo_entrante(acto.name):
                        company.update_cargos_entrantes(lista_cargos)
                    else:
                        company.update_cargos_salientes(lista_cargos)
                else:
                    # not bormeparser.borme.BormeActoCargo
                    nuevo_anuncio.actos[acto.name] = acto.value

            company.anuncios.append({'id': nuevo_anuncio.id_anuncio, 'year': nuevo_anuncio.year})
            company.date_updated = borme.date
            company.save()
            nuevo_anuncio.company = company
            nuevo_anuncio.save()
            nuevo_borme.anuncios.append(anuncio.id)

        except Exception as e:
            logger.error('[%s] ERROR importing anuncio %d' % (borme.cve, anuncio.id))
            logger.error('[X] %s: %s' % (e.__class__.__name__, e))
            results['errors'] += 1

    nuevo_borme.save()

    borme_log.errors = results['errors']
    borme_log.parsed = True  # FIXME: Si hay ValidationError, parsed = False
    borme_log.date_parsed = timezone.now()
    borme_log.save()
    return results


def get_borme_xml_filepath(date):
    year = str(date.year)
    month = '%02d' % date.month
    day = '%02d' % date.day
    filename = 'BORME-S-%s%s%s.xml' % (year, month, day)
    return os.path.join(settings.BORME_XML_ROOT, year, month, filename)


def get_borme_pdf_path(date):
    year = '%02d' % date.year
    month = '%02d' % date.month
    day = '%02d' % date.day
    return os.path.join(settings.BORME_PDF_ROOT, year, month, day)


def get_borme_json_path(date):
    year = '%02d' % date.year
    month = '%02d' % date.month
    day = '%02d' % date.day
    return os.path.join(settings.BORME_JSON_ROOT, year, month, day)


def update_previous_xml(date):
    """ Dado una fecha, comprueba si el XML anterior es definitivo y si no lo es lo descarga de nuevo """
    xml_path = get_borme_xml_filepath(date)
    bxml = BormeXML.from_file(xml_path)

    try:
        prev_xml_path = get_borme_xml_filepath(bxml.prev_borme)
        prev_bxml = BormeXML.from_file(prev_xml_path)
        if prev_bxml.is_final:
            return False

        os.unlink(prev_xml_path)
    except FileNotFoundError:
        pass
    finally:
        prev_bxml = BormeXML.from_date(bxml.prev_borme)
        prev_bxml.save_to_file(prev_xml_path)

    return True


def files_exist(files):
    return all([os.path.exists(f) for f in files])


def import_borme_download(date_from, date_to, seccion=bormeparser.SECCION.A, local_only=False, no_missing=False, abort_on_error=False, create_json=True, save_stats=False):
    """
    date_from: "2015-01-30", "init"
    date_to: "2015-01-30", "today"
    """
    if date_from == 'init':
        date_from = FIRST_BORME[2009]
    else:
        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()

    if date_to == 'today':
        date_to = datetime.date.today()
    else:
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()

    if date_from > date_to:
        raise ValueError('date_from > date_to')

    try:
        ret, _ = _import_borme_download_range2(date_from, date_to, seccion, local_only, no_missing, abort_on_error, create_json, save_stats)
        return ret
    except BormeDoesntExistException:
        logger.info('It looks like there is no BORME for this date ({}). Nothing was downloaded'.format(date_from))
        return False


def _import_borme_download_range2(begin, end, seccion, local_only, no_missing, abort_on_error, create_json, save_stats):
    """
    local_only: No se conecta a Internet. No descarga BORMEs ni incluye la URL al generar JSON.
    """
    next_date = begin
    total_results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0,
                     'total_anuncios': 0, 'total_bormes': 0, 'total_companies': 0, 'total_persons': 0, 'errors': 0}
    total_start_time = time.time()

    if save_stats:
        csv_fp = save_stats_begin()

    try:
        while next_date and next_date <= end:
            xml_path = get_borme_xml_filepath(next_date)
            try:
                bxml = BormeXML.from_file(xml_path)
                if bxml.next_borme is None:
                    bxml = BormeXML.from_date(next_date)
                    os.makedirs(os.path.dirname(xml_path), exist_ok=True)
                    bxml.save_to_file(xml_path)

            except FileNotFoundError:
                bxml = BormeXML.from_date(next_date)
                os.makedirs(os.path.dirname(xml_path), exist_ok=True)
                bxml.save_to_file(xml_path)

            # Add FileHandlers
            logpath = os.path.join(settings.BORME_LOG_ROOT, 'imports', '%02d-%02d' % (bxml.date.year, bxml.date.month))
            os.makedirs(logpath, exist_ok=True)

            fh_info_path = os.path.join(logpath, '{day:02d}_info.txt'.format(day=bxml.date.day))
            fh_info = logging.FileHandler(fh_info_path)
            fh_info.setLevel(logging.INFO)
            logger.addHandler(fh_info)

            fh_warning_path = os.path.join(logpath, '{day:02d}_warning.txt'.format(day=bxml.date.day))
            fh_warning = logging.FileHandler(fh_warning_path)
            fh_warning.setLevel(logging.WARNING)
            logger.addHandler(fh_warning)

            fh_error_path = os.path.join(logpath, '{day:02d}_error.txt'.format(day=bxml.date.day))
            fh_error = logging.FileHandler(fh_error_path)
            fh_error.setLevel(logging.ERROR)
            logger.addHandler(fh_error)

            json_path = get_borme_json_path(bxml.date)
            pdf_path = get_borme_pdf_path(bxml.date)
            os.makedirs(pdf_path, exist_ok=True)
            logger.info('============================================================')
            logger.info('Ran import_borme_download at %s' % timezone.now())
            logger.info('  Import date: %s. Section: %s' % (bxml.date.isoformat(), seccion))
            logger.info('============================================================')

            print('\nPATH: %s\nDATE: %s\nSECCION: %s\n' % (pdf_path, bxml.date, seccion))

            bormes = []
            if not local_only:
                _, files = bxml.download_borme(pdf_path, seccion=seccion)

                for filepath in files:
                    if filepath.endswith('-99.pdf'):
                        continue
                    logger.info('%s' % filepath)
                    total_results['total_bormes'] += 1
                    try:
                        bormes.append(bormeparser.parse(filepath, seccion))
                    except Exception as e:
                        logger.error('[X] Error grave en bormeparser.parse(): %s' % filepath)
                        logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                        if abort_on_error:
                            logger.error('[X] Una vez arreglado, reanuda la importación:')
                            logger.error('[X]   python manage.py importborme -f {} -t {}'.format(next_date, end))
                            return False, total_results

            else:
                cves = bxml.get_cves(bormeparser.SECCION.A)
                files_json = list(map(lambda x: os.path.join(json_path, '%s.json' % x), cves))
                files_pdf = list(map(lambda x: os.path.join(pdf_path, '%s.pdf' % x), cves))

                if files_exist(files_json):
                    for filepath in files_json:
                        logger.info('%s' % filepath)
                        total_results['total_bormes'] += 1
                        try:
                            bormes.append(bormeparser.Borme.from_json(filepath))
                        except Exception as e:
                            logger.error('[X] Error grave en bormeparser.Borme.from_json(): %s' % filepath)
                            logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                            if abort_on_error:
                                logger.error('[X] Una vez arreglado, reanuda la importación:')
                                logger.error('[X]   python manage.py importborme -f {} -t {}'.format(next_date, end))
                                return False, total_results
                elif files_exist(files_pdf):
                    for filepath in files_pdf:
                        logger.info('%s' % filepath)
                        total_results['total_bormes'] += 1
                        try:
                            bormes.append(bormeparser.parse(filepath, seccion))
                        except Exception as e:
                            logger.error('[X] Error grave en bormeparser.parse(): %s' % filepath)
                            logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                            if abort_on_error:
                                logger.error('[X] Una vez arreglado, reanuda la importación:')
                                logger.error('[X]   python manage.py importborme -f {} -t {}'.format(next_date, end))
                                return False, total_results
                else:
                    logger.error('[X] Faltan archivos PDF y JSON que no se desea descargar.')
                    logger.error('[X] JSON: %s' % ' '.join(files_json))
                    logger.error('[X] PDF: %s' % ' '.join(files_pdf))
                    if abort_on_error or no_missing:
                        return False, total_results

                    for filepath in files_json:
                        if not os.path.exists(filepath):
                            logger.warn('[X] Missing JSON: %s' % filepath)
                            continue
                        logger.info('%s' % filepath)
                        total_results['total_bormes'] += 1
                        try:
                            bormes.append(bormeparser.Borme.from_json(filepath))
                        except Exception as e:
                            logger.error('[X] Error grave en bormeparser.Borme.from_json(): %s' % filepath)
                            logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                            if abort_on_error:
                                return False, total_results

            for borme in sorted(bormes):
                total_results['total_anuncios'] += len(borme.get_anuncios())
                start_time = time.time()
                try:
                    results = _import1(borme)
                except Exception as e:
                    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0,
                               'total_companies': 0, 'total_persons': 0, 'errors': 0}
                    logger.error('[%s] Error grave en _import1:' % borme.cve)
                    logger.error('[%s] %s' % (borme.cve, e))
                    logger.error('[%s] Prueba importar manualmente en modo detallado para ver el error:' % borme.cve)
                    logger.error('[%s]   python manage.py importbormepdf %s -v 3' % (borme.cve, borme.filename))
                    if abort_on_error:
                        logger.error('[%s] Una vez arreglado, reanuda la importación:' % borme.cve)
                        logger.error('[{}]   python manage.py importborme -f {} -t {}'.format(borme.cve, next_date, end))
                        return False, total_results

                if create_json:
                    os.makedirs(json_path, exist_ok=True)
                    json_filepath = os.path.join(json_path, '%s.json' % borme.cve)
                    borme.to_json(json_filepath, include_url=not local_only)

                total_results['created_anuncios'] += results['created_anuncios']
                total_results['created_bormes'] += results['created_bormes']
                total_results['created_companies'] += results['created_companies']
                total_results['created_persons'] += results['created_persons']
                total_results['total_companies'] += results['total_companies']
                total_results['total_persons'] += results['total_persons']
                total_results['errors'] += results['errors']

                if not all(map(lambda x: x == 0, total_results.values())):
                    print_results(results, borme)
                    elapsed_time = time.time() - start_time
                    logger.info('[%s] Elapsed time: %.2f seconds' % (borme.cve, elapsed_time))

                    if save_stats:
                        save_stats_writeline(csv_fp, borme, elapsed_time, results)
                        csv_fp.flush()

            # Remove handlers
            logger.removeHandler(fh_info)
            logger.removeHandler(fh_warning)
            logger.removeHandler(fh_error)
            next_date = bxml.next_borme
    except KeyboardInterrupt:
        logger.info('\nImport aborted.')

    elapsed_time = time.time() - total_start_time
    logger.info('\nEn total se han importado {created_bormes}/{total_bormes} BORMEs, {created_anuncios}/{total_anuncios} Anuncios, '
                '{created_companies}/{total_companies} Empresas, y {created_persons}/{total_persons} Personas.'.format(**total_results))
    logger.info('Total elapsed time: {:.2f} seconds'.format(elapsed_time))

    if save_stats:
        csv_fp.close()

    return True, total_results


def import_borme_pdf(filename, create_json=True):
    """
    Import BORME PDF to database
    """
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    try:
        borme = bormeparser.parse(filename, bormeparser.SECCION.A)
        results = _import1(borme)
        if create_json:
            json_path = get_borme_json_path(borme.date)
            os.makedirs(json_path, exist_ok=True)
            json_filepath = os.path.join(json_path, '%s.json' % borme.cve)
            borme.to_json(json_filepath)
    except Exception as e:
        logger.error('[X] Error grave en bormeparser.parse(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if not all(map(lambda x: x == 0, results.values())):
        print_results(results, borme)
    return True, results


def save_stats_begin():
    filename = datetime.datetime.now().strftime('%Y_%m_%d') + '.log'  # 2016_10_05.log
    csv_path = os.path.join(settings.BORME_LOG_ROOT, 'imports_time')
    os.makedirs(csv_path, exist_ok=True)
    csv_fp = get_file(os.path.join(csv_path, filename))
    csv_fp.write('CVE,Provincia,Elapsed,n_anuncios,n_empresas,n_personas\n')
    csv_fp.flush()
    return csv_fp


def save_stats_writeline(csv_fp, borme, elapsed_time, results):
    csv_fp.write('%s,%s,%s,%s,%s,%s\n' % (borme.cve, borme.provincia, elapsed_time, results['created_anuncios'], results['created_companies'], results['created_persons']))


def import_borme_json(filename, save_stats=False):
    """
    Import BORME JSON to database
    """
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    try:
        borme = bormeparser.Borme.from_json(filename)

        if save_stats:
            csv_fp = save_stats_begin()
            start_time = time.time()

        results = _import1(borme)

        if save_stats:
            elapsed_time = time.time() - start_time
            save_stats_writeline(csv_fp, borme, elapsed_time, results)

    except Exception as e:
        logger.error('[X] Error grave en bormeparser.Borme.from_json(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if save_stats:
        csv_fp.close()

    if not all(map(lambda x: x == 0, results.values())):
        print_results(results, borme)
    return True, results


def print_results(results, borme):
    logger.info('[{cve}] Se han importado {created_bormes}/1 BORMEs, {created_anuncios}/{total_anuncios} Anuncios, '
                '{created_companies}/{total_companies} Empresas, y {created_persons}/{total_persons} Personas.'
                .format(cve=borme.cve, total_anuncios=len(borme.get_anuncios()), **results))
