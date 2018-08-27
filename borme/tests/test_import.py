from borme.models import Anuncio, Borme, Company
import borme.parser.importer
import borme.parser.logger
import borme.utils.strings

import datetime
import gzip
import logging
import os

from django.test import TestCase

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(THIS_PATH, 'files')

# Disable loggers
borme.utils.strings.logger.setLevel(logging.ERROR)
borme.parser.importer.logger.setLevel(logging.ERROR)
borme.parser.logger.logger.setLevel(logging.ERROR)


def load_borme_from_gzipped_json(filename):
    fp = gzip.open(os.path.join(FILES_PATH, filename))
    ret = borme.parser.importer.from_json_file(fp)
    fp.close()
    return ret


class TestImport(TestCase):

    def test_import_borme(self):
        """Importa un BORME-PDF"""
        filepath = os.path.join(FILES_PATH, 'BORME-A-2015-27-10.pdf')
        borme.parser.importer.from_pdf_file(filepath, create_json=False)
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        self.assertEqual(len(find), 1)
        self.assertEqual(Anuncio.objects.count(), 30)
        # Anuncios desde el 57315 al 57344
        # BORME-A-2015-27-10
        # borme = bormeparser.parse(filename, bormeparser.SECCION.A)
        # Testear:
        # results = _from_instance(borme)


class TestImport2(TestCase):

    def test_nombramientos_ceses(self):
        """Importa un BORME-JSON con Nombramientos y otro posteriormente
           con Ceses, y comprueba que cada cargo se ha contabilizado
           correctamente
        """
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        ret = load_borme_from_gzipped_json("BORME-A-2009-197-28.json.gz")
        self.assertTrue(ret)
        self.assertEqual(Company.objects.count(), 289)
        company1 = Company.objects.get(slug='labiernag-2000')
        self.assertEqual(len(company1.get_cargos_actuales()[0]), 7)
        self.assertEqual(len(company1.get_cargos_historial()[0]), 0)

        ret = load_borme_from_gzipped_json("BORME-A-2012-246-28.json.gz")
        self.assertTrue(ret)
        self.assertEqual(Company.objects.count(), 842)
        company2 = Company.objects.get(slug='labiernag-2000')
        self.assertEqual(len(company2.get_cargos_actuales()[0]), 9)
        self.assertEqual(len(company2.get_cargos_historial()[0]), 3)


class TestImportAnuncios_BORME_A_2012_246_28(TestCase):

    def setUp(self):
        load_borme_from_gzipped_json("BORME-A-2012-246-28.json.gz")

    def test_total_companies(self):
        self.assertEqual(Company.objects.count(), 559)

    def test_nombramientos_ceses(self):
        """Importa un BORME-JSON y comprueba que un anuncio con Cese y
           Nombramiento de la misma persona es procesado correctamente
           (primero Ceses y luego Nombramientos)
        """
        company = Company.objects.get(slug='ferreteria-viena')
        self.assertEqual(company.name, 'FERRETERIA VIENA')
        self.assertEqual(len(company.get_cargos_actuales()[0]), 2)
        self.assertEqual(len(company.get_cargos_historial()[0]), 2)

    def test_extincion(self):
        # Acto: "Extinción"
        company = Company.objects.get(slug='pulso-2000')
        self.assertEqual(company.is_active, False)
        self.assertEqual(company.status, 'inactive')
        self.assertEqual(company.date_extinction, datetime.date(2012, 12, 26))
