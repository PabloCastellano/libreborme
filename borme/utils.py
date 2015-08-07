from .models import Company, Borme, Anuncio, Person, CargoCompany, CargoPerson, BormeLog
from mongoengine.errors import ValidationError, NotUniqueError

from django.conf import settings
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
ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.ERROR)


def _import1(borme):
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    nuevo_borme, created = Borme.objects.get_or_create(cve=borme.cve, date=borme.date)
    if created:
        logger.info('Creando borme %s' % borme.cve)
        results['created_bormes'] += 1

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
            logger.info('%d: Importando anuncio: %s' % (n, anuncio))
            # TODO: Buscar por slug
            try:
                company, created = Company.objects.get_or_create(name=anuncio.empresa)
                if created:
                    logger.info('Creando empresa %s' % anuncio.empresa)
                    results['created_companies'] += 1
                company.in_bormes.append(nuevo_borme)
            except NotUniqueError as e:
                logger.error('ERROR creando empresa: %s' % anuncio.empresa)
                logger.error(e)
                results['errors'] += 1
                continue

            nuevo_anuncio, created = Anuncio.objects.get_or_create(borme=nuevo_borme, id_anuncio=anuncio.id, company=company)
            if created:
                logger.info('Creando anuncio %d: %s' % (anuncio.id, anuncio.empresa))
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
                                        logger.info('Creando empresa: %s' % nombre)
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
                                        logger.info('Creando persona: %s' % nombre)
                                        results['created_persons'] += 1

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

                                except NotUniqueError as e:
                                    logger.error('ERROR creando persona: %s' % nombre)
                                    logger.error(e)
                                    results['errors'] += 1
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


def import_borme_download(date):
    """
    Download and import BORME to MongoDB database

    :param filename:
    :return:
    """
    date_t = tuple(map(int, (date[0], date[1], date[2])))
    bormeparser.download_pdfs(date_t, settings.BORME_PDF_TEMP_ROOT, bormeparser.SECCION.A)

    _, _, files = next(os.walk(settings.BORME_PDF_TEMP_ROOT))

    month_path = os.path.join(date[0], date[1])
    new_path = os.path.join(settings.BORME_PDF_ROOT, month_path)
    os.makedirs(new_path, exist_ok=True)

    for filename in files:
        filepath = os.path.join(settings.BORME_PDF_TEMP_ROOT, filename)
        borme = bormeparser.parse(filepath)
        results = _import1(borme)
        newfilepath = os.path.join(new_path, filename)
        os.rename(filepath, newfilepath)
        print(newfilepath)

    print_results(results, borme)


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
    print()
    print('BORMEs creados: %d' % results['created_bormes'])
    print('Anuncios creados: %d/%d' % (results['created_anuncios'], len(borme.get_anuncios())))
    print('Empresas creadas: %d' % results['created_companies'])
    print('Personas creadas: %d' % results['created_persons'])
    return True
