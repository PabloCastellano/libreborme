from django.test import TestCase
from borme.models import Borme
from borme.parser.importer import _from_instance

import bormeparser
import datetime
import os

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(THIS_PATH, 'files')


# TODO: Mockup de:
# borme = bormeparser.parse(filename, bormeparser.SECCION.A)
# Testear: _from_instance(borme)
class TestBormeModel(TestCase):

    results = None

    @classmethod
    def setUpClass(cls):
        super(TestBormeModel, cls).setUpClass()

        filepath = os.path.join(FILES_PATH, 'BORME-A-2015-27-10.pdf')
        borme = bormeparser.parse(filepath, bormeparser.SECCION.A)
        TestBormeModel.results = _from_instance(borme)

    def test_results(self):
        self.assertEqual(self.results['created_bormes'], 1)
        self.assertEqual(self.results['created_anuncios'], 30)
        self.assertEqual(self.results['created_companies'], 29)
        self.assertEqual(self.results['created_persons'], 35)

    def test_borme_object(self):
        b = Borme.objects.get(cve='BORME-A-2015-27-10')
        self.assertEqual(b.from_reg, 57315)
        self.assertEqual(b.until_reg, 57344)
        self.assertEqual(b.date, datetime.date(2015, 2, 10))
        self.assertEqual(b.url, 'https://boe.es/borme/dias/2015/02/10/pdfs/BORME-A-2015-27-10.pdf')
        self.assertEqual(b.province, bormeparser.PROVINCIA.CACERES)
        self.assertEqual(b.section, bormeparser.SECCION.A)
