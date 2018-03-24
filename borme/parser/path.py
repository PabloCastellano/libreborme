import os

from django.conf import settings

from bormeparser.borme import BormeXML


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
    """
    Dada una fecha, comprueba si el XML anterior es definitivo y si no lo es
    lo descarga de nuevo
    """
    xml_path = get_borme_xml_filepath(date)
    bxml = BormeXML.from_file(xml_path)

    try:
        prev_xml_path = get_borme_xml_filepath(bxml.prev_borme)
        prev_bxml = BormeXML.from_file(prev_xml_path)
        if prev_bxml.is_final:
            return False

        os.unlink(prev_xml_path)
    except OSError:
        pass
    finally:
        prev_bxml = BormeXML.from_date(bxml.prev_borme)
        prev_bxml.save_to_file(prev_xml_path)

    return True


def files_exist(files):
    return all([os.path.exists(f) for f in files])
