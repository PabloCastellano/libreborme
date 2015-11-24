from .models import Company, Borme, Anuncio, Person, BormeLog

from django.conf import settings
from django.db import connection
from django.utils.text import slugify
from django.utils import timezone

import bormeparser
from bormeparser.borme import BormeXML
from bormeparser.exceptions import BormeDoesntExistException
from bormeparser.regex import is_company, is_acto_cargo_entrante, regex_empresa_tipo
from bormeparser.utils import FIRST_BORME

import datetime
import logging
import time
import os

from calendar import HTMLCalendar, monthrange

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


class LibreBormeCalendar(HTMLCalendar):

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        Este calendario tiene enlaces al día si hay Borme.
        """

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif weekday in (5, 6):
            return '<td class="day %s">%d</td>' % (self.cssclasses[weekday], day)
        elif self.today == datetime.date(self.year, self.month, day):
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day today"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day today">%d</td>' % day
        else:
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day">%d</td>' % day

    def formatmonth(self, year, month):
        self.year = year
        self.month = month
        self.today = datetime.date.today()

        _, lastday = monthrange(year, month)
        bormes = Borme.objects.filter(date__gte=datetime.date(year, month, 1), date__lte=datetime.date(year, month, lastday)).distinct('date').order_by('date')
        self.days_bormes = {}
        for borme in bormes:
            self.days_bormes[(borme.date.month, borme.date.day)] = borme

        return super(LibreBormeCalendar, self).formatmonth(year, month)


class LibreBormeAvailableCalendar(HTMLCalendar):

    def formatday(self, day, weekday):
        """
        Return a day as a table cell.
        Este calendario tiene enlaces al día si hay Borme.
        """

        if day == 0:
            return '<td class="noday">&nbsp;</td>'  # day outside month
        elif weekday in (5, 6):
            return '<td class="day %s">%d</td>' % (self.cssclasses[weekday], day)
        elif self.today == datetime.date(self.year, self.month, day):
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day today"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day today">%d</td>' % day
        else:
            if (self.month, day) in self.days_bormes:
                url = self.days_bormes[(self.month, day)].get_absolute_url()
                return '<td class="day"><a href="%s">%d</a></td>' % (url, day)
            else:
                return '<td class="day">%d</td>' % day

    def formatmonth(self, year, month, withyear=True):
        self.month = month
        return super(LibreBormeAvailableCalendar, self).formatmonth(year, month, withyear=withyear)

    def formatyear(self, theyear, bormes, width=3):
        self.year = theyear
        self.today = datetime.date.today()

        self.days_bormes = {}
        for borme in bormes:
            self.days_bormes[(borme.date.month, borme.date.day)] = borme

        return super(LibreBormeAvailableCalendar, self).formatyear(theyear, width=width)


def _import1(borme):
    """
    borme: bormeparser.Borme
    """
    logger.info('\nBORME CVE: %s (%s, %s, [%d-%d])' % (borme.cve, borme.date, borme.provincia, borme.anuncios_rango[0], borme.anuncios_rango[1]))
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0,
               'total_companies': 0, 'total_persons': 0, 'errors': 0}

    try:
        nuevo_borme = Borme.objects.get(cve=borme.cve)
    except Borme.DoesNotExist:
        nuevo_borme = Borme(cve=borme.cve, date=borme.date, url=borme.url, from_reg=borme.anuncios_rango[0],
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

    borme_embed = {'cve': nuevo_borme.cve, 'url': nuevo_borme.url}
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
                logger.debug('Creando empresa %s %s' % (empresa, tipo))
                results['created_companies'] += 1

            company.add_in_bormes(borme_embed)

            try:
                nuevo_anuncio = Anuncio.objects.get(id_anuncio=anuncio.id, year=borme.date.year)
            except Anuncio.DoesNotExist:
                nuevo_anuncio = Anuncio(id_anuncio=anuncio.id, year=borme.date.year, borme=nuevo_borme,
                                        datos_registrales=anuncio.datos_registrales)
                logger.debug('Creando anuncio %d: %s %s' % (anuncio.id, empresa, tipo))
                results['created_anuncios'] += 1

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
                                    logger.debug('Creando empresa: %s %s' % (empresa, tipo))
                                    results['created_companies'] += 1

                                c.anuncios.append(anuncio.id)
                                c.add_in_bormes(borme_embed)

                                cargo = {'title': nombre_cargo, 'name': c.fullname, 'type': 'company'}
                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'date_from': borme.date.isoformat(), 'type': 'company'}
                                    c.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'date_to': borme.date.isoformat(), 'type': 'company'}
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
                                    logger.debug('Creando persona: %s' % nombre)
                                    results['created_persons'] += 1

                                p.add_in_companies(company.fullname)
                                p.add_in_bormes(borme_embed)

                                cargo = {'title': nombre_cargo, 'name': p.name, 'type': 'person'}
                                if is_acto_cargo_entrante(acto.name):
                                    cargo['date_from'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'date_from': borme.date.isoformat()}
                                    p.update_cargos_entrantes([cargo_embed])
                                else:
                                    cargo['date_to'] = borme.date.isoformat()
                                    cargo_embed = {'title': nombre_cargo, 'name': company.fullname, 'date_to': borme.date.isoformat()}
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

            company.anuncios.append(anuncio.id)  # TODO: year
            company.date_updated = borme.date
            company.save()
            nuevo_anuncio.company = company
            nuevo_anuncio.save()
            nuevo_borme.anuncios.append(anuncio.id)  # TODO: year

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


def import_borme_download(date, seccion=bormeparser.SECCION.A, download=True):
    """
    date: "2015", "2015-01", "2015-01-30", "--init"
    """
    if date == '--init':
        begin = FIRST_BORME[2009]
        end = datetime.date.today()
    else:
        date = tuple(map(int, date.split('-')))  # TODO: exception

        if len(date) == 3:  # 2015-06-02
            begin = datetime.date(*date)
            try:
                ret, _ = _import_borme_download_range2(begin, begin, seccion, download)
                return ret
            except BormeDoesntExistException:
                logger.info('It looks like there is no BORME for this date. Nothing was downloaded')
                return False
        elif len(date) == 2:  # 2015-06
            _, lastday = monthrange(*date)
            end = datetime.date(date[0], date[1], lastday)
            try:
                begin = datetime.date(date[0], date[1], 1)
                ret, _ = _import_borme_download_range2(begin, end, seccion, download, strict=True)
            except BormeDoesntExistException:
                try:
                    begin = datetime.date(date[0], date[1], 2)
                    ret, _ = _import_borme_download_range2(begin, end, seccion, download, strict=True)
                except BormeDoesntExistException:
                    try:
                        begin = datetime.date(date[0], date[1], 3)
                        ret, _ = _import_borme_download_range2(begin, end, seccion, download, strict=True)
                    except BormeDoesntExistException:
                        begin = datetime.date(date[0], date[1], 4)
                        ret, _ = _import_borme_download_range2(begin, end, seccion, download, strict=True)
            return ret

        elif len(date) == 1:  # 2015
            begin = FIRST_BORME[date[0]]
            end = datetime.date(date[0], 12, 31)

    ret, _ = _import_borme_download_range2(begin, end, seccion, download)
    return ret


def _import_borme_download_range2(begin, end, seccion, download, strict=False, create_json=True):
    """
    strict: Para en caso de error grave
    """
    next_date = begin
    total_results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0,
                     'total_anuncios': 0, 'total_bormes': 0, 'total_companies': 0, 'total_persons': 0, 'errors': 0}
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

            except FileNotFoundError:
                bxml = BormeXML.from_date(next_date)
                os.makedirs(os.path.dirname(xml_path), exist_ok=True)
                bxml.save_to_file(xml_path)

            # Add FileHandlers
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

            json_path = get_borme_json_path(bxml.date)
            pdf_path = get_borme_pdf_path(bxml.date)
            os.makedirs(pdf_path, exist_ok=True)
            logger.info('============================================================')
            logger.info('Ran import_borme_download at %s' % timezone.now())
            logger.info('  Import date: %s. Section: %s' % (bxml.date.isoformat(), seccion))
            logger.info('============================================================')

            print('\nPATH: %s\nDATE: %s\nSECCION: %s\n' % (pdf_path, bxml.date, seccion))

            bormes = []
            if download:
                _, files = bxml.download_pdfs(pdf_path, seccion=seccion)
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
                            if strict:
                                logger.error('[X] Una vez arreglado, reanuda la importación:')
                                logger.error('[X]   python manage.py importbormetoday local')  # TODO: --from date
                                return False, total_results
                elif files_exist(files_pdf):
                    for filepath in files_pdf:
                        logger.info('%s' % filepath)
                        total_results['total_bormes'] += 1
                        try:
                            bormes.append(bormeparser.parse(filepath))
                        except Exception as e:
                            logger.error('[X] Error grave en bormeparser.parse(): %s' % filepath)
                            logger.error('[X] %s: %s' % (e.__class__.__name__, e))
                            if strict:
                                logger.error('[X] Una vez arreglado, reanuda la importación:')
                                logger.error('[X]   python manage.py importbormetoday local')  # TODO: --from date
                                return False, total_results
                else:
                    logger.error('[X] Faltan archivos PDF y JSON que no se desea descargar.')
                    return False, total_results

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

            # Remove handlers
            logger.removeHandler(fh1)
            logger.removeHandler(fh2)
            next_date = bxml.next_borme
    except KeyboardInterrupt:
        logger.info('\nImport aborted.')

    elapsed_time = time.time() - total_start_time
    logger.info('\nBORMEs creados: %d/%d' % (total_results['created_bormes'], total_results['total_bormes']))
    logger.info('Anuncios creados: %d/%d' % (total_results['created_anuncios'], total_results['total_anuncios']))
    logger.info('Empresas creadas: %d/%d' % (total_results['created_companies'], total_results['total_companies']))
    logger.info('Personas creadas: %d/%d' % (total_results['created_persons'], total_results['total_persons']))
    logger.info('Total elapsed time: %.2f seconds' % elapsed_time)

    return True, total_results


def import_borme_pdf(filename, create_json=True):
    """
    Import BORME PDF to database
    """
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    try:
        borme = bormeparser.parse(filename)
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


def import_borme_json(filename):
    """
    Import BORME JSON to database
    """
    results = {'created_anuncios': 0, 'created_bormes': 0, 'created_companies': 0, 'created_persons': 0, 'errors': 0}

    try:
        borme = bormeparser.Borme.from_json(filename)
        results = _import1(borme)
    except Exception as e:
        logger.error('[X] Error grave en bormeparser.Borme.from_json(): %s' % filename)
        logger.error('[X] %s: %s' % (e.__class__.__name__, e))

    if not all(map(lambda x: x == 0, results.values())):
        print_results(results, borme)
    return True, results


def print_results(results, borme):
    logger.info('[%s] BORMEs creados: %d/1' % (borme.cve, results['created_bormes']))
    logger.info('[%s] Anuncios creados: %d/%d' % (borme.cve, results['created_anuncios'], len(borme.get_anuncios())))
    logger.info('[%s] Empresas creadas: %d/%d' % (borme.cve, results['created_companies'], results['total_companies']))
    logger.info('[%s] Personas creadas: %d/%d' % (borme.cve, results['created_persons'], results['total_persons']))


# http://chase-seibert.github.io/blog/2012/06/01/djangopostgres-optimize-count-by-replacing-with-an-estimate.html
# TODO: exception if db engine is not postgres as in https://github.com/stephenmcd/django-postgres-fuzzycount/blob/master/fuzzycount.py
def estimate_count_fast(table):
    ''' postgres really sucks at full table counts, this is a faster version
    see: http://wiki.postgresql.org/wiki/Slow_Counting '''
    cursor = connection.cursor()
    cursor.execute("select reltuples from pg_class where relname='%s';" % table)
    row = cursor.fetchone()
    return int(row[0])
