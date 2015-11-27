from django.test import TestCase
from borme.models import Borme
from borme.utils import _import1

import bormeparser
import datetime
import os

results = None


# TODO: Mockup de:
# borme = bormeparser.parse(filename)
# Testear: _import1(borme)
class TestBormeModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):
        super(TestBormeModel, cls).setUpClass()

        global results

        path = os.path.expanduser('~/.bormes/pdf/2015/02/10/BORME-A-2015-27-10.pdf')
        borme = bormeparser.parse(path)
        results = _import1(borme)

    def test_results(self):
        global results
        self.assertEqual(results['created_bormes'], 1)
        self.assertEqual(results['created_anuncios'], 30)
        self.assertEqual(results['created_companies'], 29)
        self.assertEqual(results['created_persons'], 35)

    def test_borme_object(self):
        b = Borme.objects.get(cve='BORME-A-2015-27-10')
        self.assertEqual(b.from_reg, 57315)
        self.assertEqual(b.until_reg, 57344)
        self.assertEqual(b.date, datetime.date(2015, 2, 10))
        self.assertEqual(b.url, 'https://boe.es/borme/dias/2015/02/10/pdfs/BORME-A-2015-27-10.pdf')
        self.assertEqual(b.province, bormeparser.PROVINCIA.CACERES)
        self.assertEqual(b.section, bormeparser.SECCION.A)
