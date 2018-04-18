from borme.models import Anuncio, Borme, Company
import borme.parser.importer

import datetime
import os

from django.test import TestCase

THIS_PATH = os.path.dirname(os.path.abspath(__file__))


class TestImport(TestCase):

    def test_import_borme(self):
        filepath = os.path.expanduser('~/.bormes/pdf/2015/02/10/BORME-A-2015-27-10.pdf')
        borme.parser.importer.from_pdf_file(filepath)
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
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        json_path = os.path.join(THIS_PATH, 'files', '1_nombramientos.json')
        ret = borme.parser.importer.from_json_file(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(len(company.get_cargos_actuales()[0]), 2)
        self.assertEqual(len(company.get_cargos_historial()[0]), 0)

        json_path = os.path.join(THIS_PATH, 'files', '2_ceses.json')
        ret = borme.parser.importer.from_json_file(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(len(company.get_cargos_actuales()[0]), 0)
        self.assertEqual(len(company.get_cargos_historial()[0]), 2)


class TestImport3(TestCase):

    def test_nombramientos_ceses(self):
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        json_path = os.path.join(THIS_PATH, 'files', '3_cese_y_nombramiento.json')
        ret = borme.parser.importer.from_json_file(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(company.name, 'EMPRESA TRES')
        self.assertEqual(len(company.get_cargos_actuales()[0]), 1)
        self.assertEqual(len(company.get_cargos_historial()[0]), 2)


class TestImport4(TestCase):

    def test_extincion(self):
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        json_path = os.path.join(THIS_PATH, 'files', '4_extincion.json')
        ret = borme.parser.importer.from_json_file(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(company.name, 'EMPRESA EXTINGUIDA')
        self.assertEqual(company.is_active, False)
        self.assertEqual(company.date_extinction, datetime.date(2015, 1, 4))
        self.assertEqual(len(company.get_cargos_actuales()[0]), 0)
        self.assertEqual(len(company.get_cargos_historial()[0]), 1)
