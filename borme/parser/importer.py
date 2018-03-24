from django.conf import settings
from django.utils.text import slugify
from django.utils import timezone

import datetime
import logging
import time
import os
import bormeparser

from bormeparser.borme import BormeXML
from bormeparser.exceptions import BormeDoesntExistException
from bormeparser.regex import (
        is_company,
        is_acto_cargo_entrante,
        regex_empresa_tipo)
from bormeparser.utils import FIRST_BORME


from borme.models import Company, Borme, Anuncio, Person, BormeLog
from borme.utils.strings import slug2

from .path import (
        files_exist,
        get_borme_json_path,
        get_borme_pdf_path,
        get_borme_xml_filepath)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def _from_instance(borme):
    """Importa en la BD una instancia bormeparser.Borme

    Importa en la BD todos los datos de la instancia BORME (personas, empresas,
    anuncios, bormes) y por último crea una entrada BormeLog para marcarlo
    como parseado.

    :param borme: Instancia BORME que se va a importar en la BD
    :type borme: bormeparser.Borme
    """
    logger.info("\nBORME CVE: {} ({}, {}, [{}-{}])"
                .format(borme.cve, borme.date, borme.provincia,
                        borme.anuncios_rango[0], borme.anuncios_rango[1]))
    results = {
        'created_anuncios': 0,
        'created_bormes': 0,
        'created_companies': 0,
        'created_persons': 0,
        'total_anuncios': 0,
        'total_bormes': 0,
        'total_companies': 0,
        'total_persons': 0,
        'errors': 0
    }

    try:
        nuevo_borme = Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        nuevo_borme = Borme(cve=borme.cve, date=borme.date, url=borme.url,
                            from_reg=borme.anuncios_rango[0],
                            until_reg=borme.anuncios_rango[1],
                            province=borme.provincia.name,
                            section=borme.seccion)
        # year, type, from_page, until_page, pages
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

    borme_embed = {'cve': nuevo_borme.cve, 'url': nuevo_borme.url}
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.debug('%d: Importando anuncio: %s' % (n, anuncio))
            results['total_companies'] += 1
            empresa, tipo = regex_empresa_tipo(anuncio.empresa)
            if tipo == '':
                logger.warn("[{}]: Tipo de empresa no detectado: {}"
                            .format(borme.cve, empresa))
            slug_c = slugify(empresa)
            try:
                company = Company.objects.get(slug=slug_c)
                if company.name != empresa:
                    logger.warn("[{}] WARNING: Empresa similar. Mismo slug: {}"
                                .format(borme.cve, slug_c))
                    logger.warn("[{cve}] {0}\n"
                                "[{cve}] {1}\n"
                                .format(company.name, empresa, cve=borme.cve))
                    results['errors'] += 1
            except Company.DoesNotExist:
                company = Company(name=empresa, type=tipo)
                logger.debug('Creando empresa %s %s' % (empresa, tipo))
                results['created_companies'] += 1

            company.add_in_bormes(borme_embed)

            try:
                nuevo_anuncio = Anuncio.objects.get(id_anuncio=anuncio.id,
                                                    year=borme.date.year)
            except Anuncio.DoesNotExist:
                nuevo_anuncio = Anuncio(
                                id_anuncio=anuncio.id,
                                year=borme.date.year,
                                borme=nuevo_borme,
                                datos_registrales=anuncio.datos_registrales)
                logger.debug("Creando anuncio {}: {} {}"
                             .format(anuncio.id, empresa, tipo))
                results['created_anuncios'] += 1

            for acto in anuncio.get_borme_actos():
                logger.debug(acto.name)
                logger.debug(acto.value)
                if isinstance(acto, bormeparser.borme.BormeActoCargo):
                    lista_cargos = []
                    for nombre_cargo, nombres in acto.cargos.items():
                        logger.debug(
                                "{} {} {}"
                                .format(nombre_cargo, nombres, len(nombres)))
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
                                    logger.debug("Creando empresa: {} {}"
                                                 .format(empresa, tipo))
                                    results['created_companies'] += 1

                                c.anuncios.append(anuncio.id)
                                c.add_in_bormes(borme_embed)

                                cargo = {
                                    'title': nombre_cargo,
                                    'name': c.fullname,
                                    'type': 'company'
                                }
                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {
                                        'title': nombre_cargo,
                                        'name': company.fullname,
                                        'date_from': borme.date.isoformat(),
                                        'type': 'company'
                                    }
                                    c.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {
                                        'title': nombre_cargo,
                                        'name': company.fullname,
                                        'date_to': borme.date.isoformat(),
                                        'type': 'company'
                                    }
                                    c.update_cargos_salientes([cargo_embed])
                                c.date_updated = borme.date
                                c.save()
                            else:
                                results['total_persons'] += 1
                                slug_p = slugify(nombre)
                                try:
                                    p = Person.objects.get(slug=slug_p)
                                    if p.name != nombre:
                                        logger.warn(
                                            "[{}] WARNING: Persona similar. "
                                            "Mismo slug: {}"
                                            .format(borme.cve, slug_p))
                                        logger.warn(
                                            "[{cve}] {0}\n"
                                            "[{cve}] {1}\n"
                                            .format(p.name, nombre,
                                                    cve=borme.cve))
                                        results['errors'] += 1
                                except Person.DoesNotExist:
                                    p = Person(name=nombre)
                                    logger.debug(
                                            "Creando persona: {}"
                                            .format(nombre))
                                    results['created_persons'] += 1

                                p.add_in_companies(company.fullname)
                                p.add_in_bormes(borme_embed)

                                cargo = {
                                    'title': nombre_cargo,
                                    'name': p.name,
                                    'type': 'person'
                                }

                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {
                                        'title': nombre_cargo,
                                        'name': company.fullname,
                                        'date_from': borme.date.isoformat()
                                    }
                                    p.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {
                                        'title': nombre_cargo,
                                        'name': company.fullname,
                                        'date_to': borme.date.isoformat()
                                    }
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

                    if acto.name == 'Extinción':
                        extinguir_sociedad(company, borme.date)

            company.anuncios.append(anuncio.id)  # TODO: year
            company.date_updated = borme.date
            company.save()
            nuevo_anuncio.company = company
            nuevo_anuncio.save()
            nuevo_borme.anuncios.append(anuncio.id)  # TODO: year

        except Exception as e:
            logger.error("[{}] ERROR importing anuncio {}"
                         .format(borme.cve, anuncio.id))
            logger.error("[X] {classname}: {exception}"
                         .format(classname=e.__class__.__name__,
                                 exception=e))
            results['errors'] += 1

    nuevo_borme.save()

    borme_log.errors = results['errors']
    borme_log.parsed = True  # FIXME: Si hay ValidationError, parsed = False
    borme_log.date_parsed = timezone.now()
    borme_log.save()
    return results


def extinguir_sociedad(company, date):
    """Marca en la BD una sociedad como extinguida.

    Se llama a esta función cuando una sociedad se extingue.
    Todos los cargos vigentes pasan a la lista de cargos cesados (historial).
    Modifica los modelos Company y Person.
    company: Company object

    :param date: Fecha de la extinción
    :type date: datetime.date
    """
    company.is_active = False
    company.date_extinction = date
    company.date_updated = date

    for cargo in company.cargos_actuales_c:
        cargo['date_to'] = date.isoformat()
        company.cargos_historial_c.append(cargo)
        c_cesada = Company.objects.get(slug=slug2(cargo['name']))
        c_cesada._cesar_cargo(company.fullname, date.isoformat())
        c_cesada.save()

    for cargo in company.cargos_actuales_p:
        cargo['date_to'] = date.isoformat()
        company.cargos_historial_p.append(cargo)
        p_cesada = Person.objects.get(slug=slug2(cargo['name']))
        p_cesada._cesar_cargo(company.fullname, date.isoformat())
        p_cesada.save()

    company.cargos_actuales_c = []
    company.cargos_actuales_p = []
    company.save()


def import_borme_download(date_from, date_to, seccion=bormeparser.SECCION.A,
                          local_only=False, no_missing=False):
    """Descarga e importa BORMEs desde la web del Registro Mercantil.

    Descarga BORMEs en formato PDF de la web del Registro Mercantil para
    un rango de fechas, los convierte a formato BORME-JSON e importa los
    datos en la BD.

    :param date_from: Fecha desde la que importar ("2015-01-30", "init")
    :param date_to: Fecha hasta la que importar ("2015-01-30", "today")
    :param seccion: Seccion del BORME
    :param local_only: No descarga archivos, solo procesa archivos ya presentes
    :param no_missing: Aborta el proceso tan pronto como se encuentre un error
    :type date_from: str
    :type date_to: str
    :type seccion: bormeparser.SECCION
    :type local_only: bool
    :type no_missing: bool
    """
    if date_from == 'init':
        date_from = FIRST_BORME[2009]
    else:
        date = tuple(map(int, date_from.split('-')))  # TODO: exception
        date_from = datetime.date(*date)

    if date_to == 'today':
        date_to = datetime.date.today()
    else:
        date = tuple(map(int, date_to.split('-')))  # TODO: exception
        date_to = datetime.date(*date)

    if date_from > date_to:
        raise ValueError('date_from > date_to')

    try:
        ret, _ = _import_borme_download_range(date_from, date_to, seccion,
                                              local_only, strict=no_missing)
        return ret
    except BormeDoesntExistException:
        logger.info("It looks like there is no BORME for this date ({}). "
                    "Nothing was downloaded".format(date_from))
        return False


def _load_and_append(files_list, strict, seccion=bormeparser.SECCION.A):
    """Procesa una lista de archivos BORME.

    Procesa una lista de archivos BORME (JSON o PDF) y devuelve una lista
    con sus instancias.

    :rtype: ([borme], error bool)
    """
    bormes = []

    if files_list[0].endswith("json"):
        file_format = "json"
        parse_func = bormeparser.Borme.from_json
    else:
        file_format = "pdf"
        parse_func = bormeparser.parse

    for filepath in files_list:

        if not os.path.exists(filepath):
            logger.warn('[X] Missing JSON: %s' % filepath)
            continue
        logger.info(filepath)

        try:
            if file_format == "json":
                borme = parse_func(filepath)
            else:
                borme = parse_func(filepath, seccion)
            bormes.append(borme)

        except Exception as e:
            logger.error("[X] Error grave (I) en {obj}.{method}: {path}"
                         .format(obj=parse_func.__objclass__,
                                 method=parse_func.__name__,
                                 path=filepath))
            logger.error("[X] {}: {}"
                         .format(e.__class__.__name__, e))
            if strict:
                logger.error('[X] Una vez arreglado, reanuda la importación:')
                # TODO: --from date
                logger.error('[X]   python manage.py importbormetoday local')
                return bormes, True

    return bormes, False


def _generate_borme_files_list(bxml, json_path, pdf_path):
    cves = bxml.get_cves(bormeparser.SECCION.A)
    files_json = map(lambda x: os.path.join(json_path, '%s.json' % x), cves)
    files_pdf = map(lambda x: os.path.join(pdf_path, '%s.pdf' % x), cves)
    return list(files_json), list(files_pdf)


def _import_borme_download_range(begin, end, seccion, local_only,
                                 strict=False, create_json=True):
    """Importa los BORMEs data un rango de fechas.

    Itera en el rango de fechas. Por cada día:
    * Genera los nombres de los archivos BORMEs a partir del archivo BORME-XML
    * Carga los archivos BORME-JSON, o los BORME-PDF si no existieran los JSON
    * Importa en la BD los datos de los BORME

    :param begin: Fecha desde la que importar
    :param end: Fecha hasta la que importar
    :param seccion: Seccion del BORME
    :param local_only: No descarga archivos, solo procesa archivos ya presentes
    :param strict: Aborta el proceso tan pronto como se encuentre un error
    :param create_json: Crear archivo BORME-JSON
    :type date_from: datetime.date
    :type date_to: datetime.date
    :type seccion: bormeparser.SECCION
    :type local_only: bool
    :type strict: bool
    :type create_json: bool

    :rtype: (bool, dict)
    """
    next_date = begin
    total_results = {
        'created_anuncios': 0,
        'created_bormes': 0,
        'created_companies': 0,
        'created_persons': 0,
        'total_anuncios': 0,
        'total_bormes': 0,
        'total_companies': 0,
        'total_persons': 0,
        'errors': 0
    }
    total_start_time = time.time()

    try:
        while next_date and next_date <= end:
            xml_path = get_borme_xml_filepath(next_date)
            try:
                bxml = BormeXML.from_file(xml_path)
                if bxml.next_borme is None:
                    bxml = BormeXML.from_date(next_date)
                    os.makedirs(os.path.dirname(xml_path), exist_ok=True)
                    bxml.save_to_file(xml_path)

            except OSError:
                bxml = BormeXML.from_date(next_date)
                os.makedirs(os.path.dirname(xml_path), exist_ok=True)
                bxml.save_to_file(xml_path)

            # Add FileHandlers
            directory = '%02d-%02d' % (bxml.date.year, bxml.date.month)
            logpath = os.path.join(settings.BORME_LOG_ROOT,
                                   'imports', directory)
            os.makedirs(logpath, exist_ok=True)

            fh1_path = os.path.join(logpath, '%02d_info.txt' % bxml.date.day)
            fh1 = logging.FileHandler(fh1_path)
            fh1.setLevel(logging.INFO)
            logger.addHandler(fh1)

            fh2_path = os.path.join(logpath, '%02d_error.txt' % bxml.date.day)
            fh2 = logging.FileHandler(fh2_path)
            fh2.setLevel(logging.WARNING)
            logger.addHandler(fh2)

            json_path = get_borme_json_path(bxml.date)
            pdf_path = get_borme_pdf_path(bxml.date)
            os.makedirs(pdf_path, exist_ok=True)
            logger.info(
                    "===================================================\n"
                    "Ran import_borme_download at {now}\n"
                    "  Import date: {borme_date}. Section: {section}\n"
                    "==================================================="
                    .format(now=timezone.now(), section=seccion,
                            borme_date=bxml.date.isoformat()))
            print("\nPATH: {}"
                  "\nDATE: {}"
                  "\nSECCION: {}\n"
                  .format(pdf_path, bxml.date, seccion))

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
                        logger.error('[X] Error grave (I) en bormeparser.parse(): %s' % filepath)
                        logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                        if strict:
                            logger.error('[X] Una vez arreglado, reanuda la importación:')
                            logger.error('[X]   python manage.py importbormetoday local')
                            return False, total_results

            else:
                files_json, files_pdf = _generate_borme_files_list(bxml,
                                                                   json_path,
                                                                   pdf_path)

                if files_exist(files_json):
                    bormes, err = _load_and_append(files_json, strict)
                    total_results["total_bormes"] += len(bormes)

                    if err:
                        return False, total_results

                elif files_exist(files_pdf):
                    bormes, err = _load_and_append(files_pdf, strict, seccion)
                    total_results["total_bormes"] += len(bormes)

                    if err:
                        return False, total_results
                else:
                    logger.error('[X] Faltan archivos PDF y JSON que no se desea descargar.')
                    logger.error('[X] JSON: %s' % ' '.join(files_json))
                    logger.error('[X] PDF: %s' % ' '.join(files_pdf))

                    if strict:
                        return False, total_results

                    bormes, err = _load_and_append(files_pdf, strict, seccion)
                    total_results["total_bormes"] += len(bormes)

            for borme in sorted(bormes):
                total_results['total_anuncios'] += len(borme.get_anuncios())
                start_time = time.time()
                try:
                    results = _import1(borme)
                except Exception as e:
                    logger.error('[%s] Error grave en _import1:' % borme.cve)
                    logger.error('[%s] %s' % (borme.cve, e))
                    logger.error('[%s] Prueba importar manualmente en modo detallado para ver el error:' % borme.cve)
                    logger.error('[%s]   python manage.py importbormepdf %s -v 3' % (borme.cve, borme.filename))
                    if strict:
                        logger.error('[%s] Una vez arreglado, reanuda la importación:' % borme.cve)
                        logger.error('[%s]   python manage.py importbormetoday local' % borme.cve)
                        return False, total_results

                if create_json:
                    os.makedirs(json_path, exist_ok=True)
                    json_filepath = os.path.join(json_path, '%s.json' % borme.cve)
                    borme.to_json(json_filepath)

                for key in total_results.keys():
                    total_results[key] += results[key]

                if not all(map(lambda x: x == 0, total_results.values())):
                    _print_results(results, borme)
                    elapsed_time = time.time() - start_time
                    logger.info('[%s] Elapsed time: %.2f seconds' % (borme.cve, elapsed_time))

            # Remove handlers
            logger.removeHandler(fh1)
            logger.removeHandler(fh2)
            next_date = bxml.next_borme
    except KeyboardInterrupt:
        logger.info('\nImport aborted.')

    elapsed_time = time.time() - total_start_time
    logger.info("\nBORMEs creados: {created_bormes}/{total_bormes}\n"
                "Anuncios creados: {created_anuncios}/{total_anuncios}\n"
                "Empresas creadas: {created_companies}/{total_companies}\n"
                "Personas creadas: {created_persons}/{total_persons}"
                .format(**total_results))
    logger.info("Total elapsed time: %.2f seconds" % elapsed_time)

    return True, total_results


def from_pdf_file(filename, create_json=True):
    """Importa un archivo BORME-PDF en la BD.

    :param filename: Archivo a importar
    :param create_json: Crear BORME-JSON como paso intermedio
    :type filename: str
    :type create_json: bool
    :rtype: (bool, dict)
    """
    results = {
        'created_anuncios': 0,
        'created_bormes': 0,
        'created_companies': 0,
        'created_persons': 0,
        'errors': 0
    }

    try:
        borme = bormeparser.parse(filename, bormeparser.SECCION.A)
        results = _from_instance(borme)
        if create_json:
            json_path = get_borme_json_path(borme.date)
            os.makedirs(json_path, exist_ok=True)
            json_filepath = os.path.join(json_path, '%s.json' % borme.cve)
            borme.to_json(json_filepath)
    except Exception as e:
        logger.error('[X] Error grave (III) en bormeparser.parse(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if not all(map(lambda x: x == 0, results.values())):
        _print_results(results, borme)
    return True, results


def from_json_file(filename):
    """Importa un archivo BORME-JSON en la BD.

    :param filename: Archivo a importar
    :type filename: str
    :rtype: (bool, dict)
    """
    results = {
        'created_anuncios': 0,
        'created_bormes': 0,
        'created_companies': 0,
        'created_persons': 0,
        'errors': 0
    }

    try:
        borme = bormeparser.Borme.from_json(filename)
        results = _from_instance(borme)
    except Exception as e:
        logger.error('[X] Error grave (III) en bormeparser.Borme.from_json(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if not all(map(lambda x: x == 0, results.values())):
        _print_results(results, borme)
    return True, results


def _print_results(results, borme):
    """Muestra un resumen del proceso de importación.

    Una vez finalizado el proceso de importación, muestra un resumen con los
    números de bormes, anuncios, empresas y personas importados.

    :param results: Diccionario que contiene los resultados del proceso
    :param borme: Instancia BORME
    :type results: dict.Borme
    :type borme: bormeparser.Borme
    """
    log_message = "[{cve}] BORMEs creados: {bormes}/1\n" \
                  "[{cve}] Anuncios creados: {anuncios}/{total_anuncios}\n" \
                  "[{cve}] Empresas creadas: {companies}/{total_companies}\n" \
                  "[{cve}] Personas creadas: {persons}/{total_persons}" \
                  .format(cve=borme.cve, bormes=results['created_bormes'],
                          anuncios=results['created_anuncios'],
                          total_anuncios=len(borme.get_anuncios()),
                          companies=results['created_companies'],
                          total_companies=results['total_companies'],
                          persons=results['created_persons'],
                          total_persons=results['total_persons'])
    logger.info(log_message)
