from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date

import datetime
import logging
import time
import os
import bormeparser

from bormeparser.borme import BormeXML
from bormeparser.exceptions import BormeDoesntExistException
from bormeparser.regex import is_company
from bormeparser.utils import FIRST_BORME

from importlib import import_module

from borme.models import (
        anuncio_get_or_create,
        borme_get_or_create,
        bormelog_get_or_create,
        company_get_or_create,
        person_get_or_create,
)

from . import actos
from .logger import (
        logger_acto,
        logger_anuncio_create,
        logger_borme_create,
        logger_cargo,
        logger_empresa_similar,
        logger_empresa_create,
        logger_persona_create,
        logger_persona_similar,
        logger_resume_import,
)
from .path import (
        files_exist,
        get_borme_json_path,
        get_borme_pdf_path,
        get_borme_xml_filepath
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _importar_cargos(nombres, nombre_cargo, borme, borme_embed, anuncio, acto,
                     company, lista_cargos, results):

    if nombre_cargo == 'Auditor' and len(nombres) != 1:
        logger.warn("Lista de auditores > 1")

    for nombre in nombres:
        logger.debug('  %s' % nombre)
        if is_company(nombre):
            type_ = 'company'
            results['total_companies'] += 1
        else:
            type_ = 'person'
            results['total_persons'] += 1

        cargo, created = _load_cargo(nombre, nombre_cargo, borme, borme_embed,
                                     company, anuncio, acto, type_)

        if not created:
            results["errors"] += 1
        else:
            if type_ == 'company':
                results["created_companies"] += 1
            else:
                results["created_persons"] += 1

        lista_cargos.append(cargo)


# TODO: retrieve_url offline
def _from_instance(borme, set_url=True):
    """Importa en la BD una instancia borme.parser.backend.BormeBase

    Importa en la BD todos los datos de la instancia BORME (personas, empresas,
    anuncios, bormes) y por último crea una entrada BormeLog para marcarlo
    como parseado.

    :param borme: Instancia BORME que se va a importar en la BD
    :type borme: bormeparser.parser.backend.BormeBase
    """
    logger.info("Importing {cve} ({date}, {provincia}, [{first}-{last}])"
                .format(cve=borme.cve,
                        date=borme.date,
                        provincia=borme.provincia,
                        first=borme.anuncios_rango[0],
                        last=borme.anuncios_rango[1]))
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

    # Create borme

    nuevo_borme, created = borme_get_or_create(borme)

    # Returns IOError for yabormeparser if xml doesn't exist
    try:
        if nuevo_borme.url is None:
            xml_path = get_borme_xml_filepath(borme.date)
            bxml = BormeXML.from_file(xml_path)
            nuevo_borme.url = bxml.get_url_cve(borme.cve)
    except IOError as e:
        logger.warn("Could not locate BORME-XML: " + xml_path)
        if set_url:
            raise
        nuevo_borme.url = ""

    if created:
        logger_borme_create(borme.cve)
        results['created_bormes'] += 1

    # Create bormelog

    borme_log, _ = bormelog_get_or_create(nuevo_borme)
    if borme_log.parsed:
        logger.warn('%s ya ha sido analizado.' % borme.cve)
        return results

    borme_log.save()  # date_updated

    borme_embed = {'cve': nuevo_borme.cve, 'url': nuevo_borme.url}
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.debug('%d: Importando anuncio: %s' % (n, anuncio))
            results['total_companies'] += 1

            # Create empresa
            company, created = company_get_or_create(anuncio.empresa)

            if company.type == '':
                logger.warn("[{}] Tipo de empresa no detectado: {}"
                            .format(borme.cve, anuncio.empresa))

            if created:
                logger_empresa_create(company.fullname)
                results["created_companies"] += 1
            else:
                if company.name != anuncio.empresa:
                    logger_empresa_similar(company, anuncio.empresa, borme.cve)
                results["errors"] += 1

            # Create anuncio
            nuevo_anuncio, created = anuncio_get_or_create(anuncio,
                                                           borme.date.year,
                                                           nuevo_borme)

            if created:
                logger_anuncio_create(anuncio.id, company)
                results['created_anuncios'] += 1

            company.add_in_bormes(borme_embed)
            company.anuncios.append({"year": borme.date.year,
                                     "id": anuncio.id})
            company.date_updated = nuevo_anuncio.date

            for acto in anuncio.get_borme_actos():
                logger_acto(acto)

                # Nombramientos, Reelecciones
                # Modificación de poderes, Revocaciones, Ceses/Dimisiones,
                # Cancelaciones de oficio de nombramientos
                if acto.is_acto_cargo():
                    lista_cargos = []
                    for nombre_cargo, nombres in acto.roles.items():
                        logger_cargo(nombre_cargo, nombres)
                        _importar_cargos(
                                nombres, nombre_cargo, borme, borme_embed,
                                anuncio, acto, company,
                                lista_cargos, results)

                    nuevo_anuncio.actos.append([acto.name, lista_cargos])

                    # No incluir en la tabla de cargos los Auditores, ya
                    # que no suelen ser cesados. Mostrar solo el acto.
                    lista_cargos = filter(lambda c: c['title'] != 'Auditor',
                                          lista_cargos)

                    if actos.is_acto_cargo_entrante(acto.name):
                        company.update_cargos_entrantes(lista_cargos)
                    else:
                        company.update_cargos_salientes(lista_cargos)
                else:
                    nuevo_anuncio.actos.append([acto.name, acto._acto])

                    if acto.name == 'Constitución':
                        actos.constitucion_sociedad(company, acto, nuevo_anuncio.date)
                    elif acto.name == 'Ampliación de capital':
                        company.capital = acto.resultante_suscrito
                    elif acto.name == 'Reducción de capital':
                        # company.capital = acto.resultante
                        pass
                    elif acto.name == 'Sociedad unipersonal':
                        pass
                    elif acto.name == 'Declaración de unipersonalidad':
                        pass
                    elif acto.name == 'Página web de la sociedad':
                        # company.url
                        pass
                    elif acto.name == 'Cambio de domicilio social':
                        company.domicilio = acto.value
                    elif acto.name == 'Cambio de objeto social':
                        company.objeto = acto.value
                    elif acto.name == 'Articulo 378.5 del Reglamento del Registro Mercantil':
                        # company.status
                        pass
                    elif acto.name == 'Reactivación de la sociedad (Art. 242 del Reglamento del Registro Mercantil)':
                        # company.status
                        pass
                    elif actos.is_acto_cierre_hoja_registral(acto.name):
                        actos.suspender_sociedad(company)
                    elif actos.is_acto_reapertura_hoja_registral(acto.name):
                        actos.activar_sociedad(company)
                    elif acto.name == 'Extinción':
                        actos.extinguir_sociedad(company, nuevo_anuncio.date)
                    elif acto.name == 'Disolución':
                        actos.disolver_sociedad(company, nuevo_anuncio.date, acto.value)
                    elif acto.name == 'Cambio de denominación social':
                        # company_new_name = acto.denominacion
                        pass
                    elif acto.name == 'Transformación de sociedad':
                        # actos.transformacion_sociedad(company, acto.denominacion)
                        pass

            company.save()
            nuevo_anuncio.company = company
            nuevo_anuncio.save()
            # FIXME: year is not needed as we have a borme date already
            nuevo_borme.anuncios.append({"year": borme.date.year,
                                         "id": anuncio.id})

        except Exception as e:
            logger.exception("In {} importing anuncio {}".format(borme.cve, anuncio.id))
            results['errors'] += 1

    nuevo_borme.save()

    borme_log.errors = results['errors']
    borme_log.parsed = True  # FIXME: Si hay ValidationError, parsed = False
    borme_log.date_parsed = timezone.now()
    borme_log.save()
    return results


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
        date_from = parse_date(date_from)

    if date_to == 'today':
        date_to = datetime.date.today()
    else:
        date_to = parse_date(date_to)

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

    # TODO: remove PDF support, just parse JSON
    # TODO: yabormeparser and pdf not supported at the moment
    # TODO: Use django.utils.module_loading.import_string()
    if files_list[0].endswith("json"):
        file_format = "json"
        parse_func = import_module(settings.PARSER).Borme.from_json
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
            logger.exception("Parsing file {}".format(filepath))
            if strict:
                logger_resume_import()
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

            json_path = get_borme_json_path(bxml.date)
            pdf_path = get_borme_pdf_path(bxml.date)
            os.makedirs(pdf_path, exist_ok=True)
            logger.info("===================================================")
            logger.info("Ran import_borme_download at {}".format(timezone.now()))
            logger.info("PATH: {}".format(pdf_path))
            logger.info("DATE: {}".format(bxml.date.isoformat()))
            logger.info("SECCION: {}".format(seccion))

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
                        logger.exception("Parsing file {}".format(filepath))
                        if strict:
                            logger_resume_import()
                            return False, total_results

            else:
                files_json, files_pdf = _generate_borme_files_list(bxml,
                                                                   json_path,
                                                                   pdf_path)

                if files_exist(files_json):
                    bormes, err = _load_and_append(files_json, strict)
                    total_results["total_bormes"] += len(files_json)

                    if err:
                        return False, total_results

                elif files_exist(files_pdf):
                    bormes, err = _load_and_append(files_pdf, strict, seccion)
                    total_results["total_bormes"] += len(files_pdf)

                    if err:
                        return False, total_results
                else:
                    logger.error('[X] Faltan archivos PDF y JSON que no se desea descargar.')
                    logger.error('[X] JSON: %s' % ' '.join(files_json))
                    logger.error('[X] PDF: %s' % ' '.join(files_pdf))

                    if strict:
                        return False, total_results

                    bormes, err = _load_and_append(files_pdf, strict, seccion)
                    total_results["total_bormes"] += len(files_pdf)

            for borme in sorted(bormes):
                total_results['total_anuncios'] += len(borme.get_anuncios())
                start_time = time.time()
                try:
                    results = _from_instance(borme)
                except Exception as e:
                    logger.error('[%s] Error grave en _from_instance:' % borme.cve)
                    logger.error('[%s] %s' % (borme.cve, e))
                    logger.error('[%s] Prueba importar manualmente en modo detallado para ver el error:' % borme.cve)
                    logger.error('[%s]   python manage.py importbormepdf %s -v 3' % (borme.cve, borme.filename))
                    if strict:
                        logger_resume_import(cve=borme.cve)
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


def from_json_file(filename, set_url=True):
    """Importa un archivo BORME-JSON en la BD.

    :param filename: Archivo a importar
    :type filename: str or file
    :rtype: (bool, dict)
    """
    results = {
        'created_anuncios': 0,
        'created_bormes': 0,
        'created_companies': 0,
        'created_persons': 0,
        'errors': 0
    }

    # TODO: Use django.utils.module_loading.import_string()
    parse_func = import_module(settings.PARSER).Borme.from_json

    try:
        borme = parse_func(filename)
        results = _from_instance(borme, set_url)
    except Exception as e:
        logger.exception("Parsing {}".format(filename))

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
    log_message = "In {cve} BORME:{bormes}/1, Anuncios:{anuncios}/{total_anuncios}, Empresas:{companies}/{total_companies}, Personas:{persons}/{total_persons}" \
                  .format(cve=borme.cve, bormes=results['created_bormes'],
                          anuncios=results['created_anuncios'],
                          total_anuncios=len(borme.get_anuncios()),
                          companies=results['created_companies'],
                          total_companies=results['total_companies'],
                          persons=results['created_persons'],
                          total_persons=results['total_persons'])
    logger.info(log_message)


def _load_cargo(nombre, nombre_cargo, borme, borme_embed, company,
                anuncio, acto, type_):
    """Importa en la BD la persona o empresa que aparece en un cargo.

    Inserta la persona/empresa si no existe e inserta los cargos.
    Actualiza las fechas de entrada/salida del cargo.

    :rtype: (dict, bool cargo created)
    """

    if type_ == 'person':
        entity, created = person_get_or_create(nombre)
    else:
        entity, created = company_get_or_create(nombre)

    if created:
        if type_ == 'person':
            logger_persona_create(nombre)
        else:
            logger_empresa_create(entity.fullname)
    else:
        if type_ == 'person':
            if entity.name != nombre:
                logger_persona_similar(entity.slug, entity.name,
                                       nombre, borme.cve)
        else:
            if entity.name != nombre:
                logger_empresa_similar(entity, nombre, borme.cve)

    if type_ == 'person':
        entity.add_in_companies(company.fullname)
    else:
        entity.anuncios.append({"year": borme.date.year, "id": anuncio.id})
    entity.add_in_bormes(borme_embed)
    entity.date_updated = borme.date

    cargo = {'title': nombre_cargo, 'type': type_}
    if type_ == 'person':
        cargo['name'] = entity.name
    else:
        cargo['name'] = entity.fullname
    if actos.is_acto_cargo_entrante(acto.name):
        cargo['date_from'] = borme.date.isoformat()
    else:
        cargo['date_to'] = borme.date.isoformat()

    if nombre_cargo == 'Auditor':
        company.add_auditor(nombre, type_, borme.date.isoformat())
    if nombre_cargo in ('Liquidador', 'LiquiSoli'):
        company.add_liquidator(nombre, type_, borme.date.isoformat())
    else:
        cargo_embed = {'title': nombre_cargo, 'name': company.fullname}

        if type_ == 'company':
            cargo_embed['type'] = 'company'

        if actos.is_acto_cargo_entrante(acto.name):
            cargo_embed["date_from"] = borme.date.isoformat()
            entity.update_cargos_entrantes([cargo_embed])
        else:
            cargo_embed["date_to"] = borme.date.isoformat()
            entity.update_cargos_salientes([cargo_embed])

    entity.save()

    return cargo, created
