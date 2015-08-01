from .models import Company, Borme, Anuncio, Person, CargoCompany, CargoPerson
from mongoengine.errors import ValidationError, NotUniqueError

import bormeparser
from bormeparser.regex import is_company, is_acto_cargo_entrante

from django.conf import settings

import six
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
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0}

    nuevo_borme, created = Borme.objects.get_or_create(cve=borme.cve)
    if created:
        logger.info('Creando borme %s' % borme.cve)
        results['created_bormes'] += 1

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
                                    cargo = CargoCompany(titulo=nombre_cargo, nombre=c)
                                    lista_cargos.append(cargo)
                                except NotUniqueError as e:
                                    logger.error('ERROR creando empresa: %s' % nombre)
                                    logger.error(e)

                            else:
                                try:
                                    p, created = Person.objects.get_or_create(name=nombre)
                                    if created:
                                        logger.info('Creando persona: %s' % nombre)
                                        results['created_persons'] += 1

                                    p.in_companies.append(company)
                                    p.in_bormes.append(nuevo_borme)
                                    cargo = CargoPerson(titulo=nombre_cargo, nombre=p)
                                    lista_cargos.append(cargo)
                                    cargo = CargoCompany(titulo=nombre_cargo, nombre=company)
                                    if is_acto_cargo_entrante(acto.name):
                                        p.update_cargos_entrantes([cargo])
                                    else:
                                        p.update_cargos_salientes([cargo])
                                    p.save()

                                except NotUniqueError as e:
                                    logger.error('ERROR creando persona: %s' % nombre)
                                    logger.error(e)

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

        nuevo_borme.save()
    return results


def import_borme_download(date):
    """
    Download and import BORME to MongoDB database

    :param filename:
    :return:
    """
    date_t = tuple(map(int, (date[0], date[1], date[2])))
    bormeparser.download_pdfs(date_t, settings.BORME_PDF_TEMP_ROOT, bormeparser.SECCION.A)

    if six.PY3:
        _, _, files = next(os.walk(settings.BORME_PDF_TEMP_ROOT))
    else:
        _, _, files = os.path.walk(settings.BORME_PDF_TEMP_ROOT).next()

    month_path = os.path.join(date[0], date[1])
    new_path = os.path.join(settings.BORME_PDF_ROOT, month_path)
    if six.PY3:
        os.makedirs(new_path, exist_ok=True)
    else:
        try:
            os.makedirs(new_path)
        except OSError:
            pass

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
