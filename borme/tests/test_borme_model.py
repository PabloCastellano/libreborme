from django.test import TestCase
from borme.models import Borme

import bormeparser
import datetime
import os

b1_id = None


# Hacer Mockup de:
# borme = bormeparser.parse(filename)
# Testear: _import1(borme)
class TestBormeModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):
        super(TestBormeModel, cls).setUpClass()

        global b1_id

        path = os.path.expanduser('~/.bormes/pdf/2015/02/10/BORME-A-2015-27-10.pdf')
        b1 = bormeparser.parse(path)
        b1.save()

        # Save the id of objects to match in the test
        b1_id = b1.id

    @classmethod
    def tearDownClass(cls):
        Borme.objects.all().delete()
        super(TestBormeModel, cls).tearDownClass()

    # This method run on every test
    def setUp(self):
        global b1_id
        self.b1_id = b1_id

    def test_borme_object(self):
        b = Borme.objects.get(cve='BORME-A-2015-27-10')
        self.assertEqual(b.from_reg, 57315)
        self.assertEqual(b.until_reg, 57344)
        self.assertEqual(b.date, datetime.date(2015, 2, 10))
        self.assertEqual(b.url, 'http://boe.es/borme/dias/2015/02/10/pdfs/BORME-A-2015-27-10.pdf')
        self.assertEqual(b.province, bormeparser.PROVINCIA.CACERES)
        self.assertEqual(b.section, bormeparser.SECCION.A)
