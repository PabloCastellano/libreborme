from .models import Company, Borme, Anuncio, Person, CargoCompany, CargoPerson
from mongoengine.errors import ValidationError, NotUniqueError

import bormeparser
from bormeparser.regex import is_company

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
#logger.setLevel(logging.INFO)
logger.setLevel(logging.ERROR)


def _import1(borme):
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0}
    try:
        nuevo_borme = Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        logger.info('Creando borme %s' % borme.cve)
        results['created_bormes'] += 1
        nuevo_borme = Borme(cve=borme.cve, date=borme.date, url=borme.url, province=borme.provincia, section=borme.seccion).save()

    # TODO: borrar si hubieran actos para este borme?
    for n, anuncio in enumerate(borme.get_anuncios(), 1):
        try:
            logger.info('%d: Importando anuncio: %s' % (n, anuncio))
            #company = Company.objects.get_or_create(name=acto.empresa)
            #if not Company.objects.exists(name=acto.empresa):
            try:
                company = Company.objects.get(name=anuncio.empresa)
            except Company.DoesNotExist:
                logger.info('Creando empresa %s' % anuncio.empresa)
                results['created_companies'] += 1
                company = Company(name=anuncio.empresa)
            company.in_bormes.append(nuevo_borme)
            try:
                company.save()
            except NotUniqueError as e:
                logger.error('ERROR creando empresa: %s' % anuncio.empresa)
                logger.error(e)
                continue

            try:
                nuevo_anuncio = Anuncio.objects.get(borme=nuevo_borme, id_anuncio=anuncio.id)
            except Anuncio.DoesNotExist:
                logger.info('Creando anuncio %d %s:' % (anuncio.id, anuncio.empresa))
                nuevo_anuncio = Anuncio(company=company, borme=nuevo_borme, id_anuncio=anuncio.id)
                results['created_anuncios'] += 1

            for acto in anuncio.get_borme_actos():
                #logger.debug(acto.name)
                #logger.debug(acto.value)
                if isinstance(acto, bormeparser.borme.BormeActoCargo):
                    for cargo, nombres in acto.cargos.items():
                        #logger.debug(cargo, nombres, len(nombres))
                        l = []
                        for nombre in nombres:
                            #logger.debug('  %s' % nombre)
                            if is_company(nombre):
                                try:
                                    c = Company.objects.get(name=nombre)
                                except Company.DoesNotExist:
                                    logger.info('Creando empresa: %s' % nombre)
                                    results['created_companies'] += 1
                                    c = Company(name=nombre)

                                # TODO: relations
                                try:
                                    c.save()
                                    l.append(CargoCompany(titulo=cargo, nombre=c))
                                except NotUniqueError as e:
                                    logger.error('ERROR creando empresa: %s' % nombre)
                                    logger.error(e)

                            else:
                                try:
                                    p = Person.objects.get(name=nombre)
                                except Person.DoesNotExist:
                                    logger.info('Creando persona: %s' % nombre)
                                    results['created_persons'] += 1
                                    p = Person(name=nombre)

                                p.in_companies.append(company)
                                p.in_bormes.append(nuevo_borme)
                                try:
                                    p.save()
                                    l.append(CargoPerson(titulo=cargo, nombre=p))
                                except NotUniqueError as e:
                                    logger.error('ERROR creando persona: %s' % nombre)
                                    logger.error(e)

                        kk = acto.name.replace('.', '||')
                        nuevo_anuncio.actos[kk] = l

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

        except ValidationError as e:
            logger.error('ERROR importing borme')
            logger.error(e)
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
