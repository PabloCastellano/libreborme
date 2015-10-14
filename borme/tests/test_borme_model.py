from django.test import TestCase
from borme.models import Borme

import bormeparser
import datetime

b1_id = None


# Hacer Mockup de:
# borme = bormeparser.parse(filename)
# Testear: _import1(borme)
class TestBormeModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):

        global b1_id

        # Create two objects for test
        b1 = Borme(cve='BORME-A-2015-27-10',  date=datetime.date(2015, 2, 10),
                   url='http://boe.es/borme/dias/2015/02/10/pdfs/BORME-A-2015-27-10.pdf',
                   province=bormeparser.PROVINCIA.CACERES.code, section='A')
        b1.save()

        # Save the id of objects to match in the test
        b1_id = b1.id

    @classmethod
    def tearDownClass(cls):
        Borme.objects.delete()
        super(TestBormeModel, cls).tearDownClass()

    # This method run on every test
    def setUp(self):
        global b1_id
        self.b1_id = b1_id
        super(TestBormeModel, self).setUp()

    def test_borme_object(self):
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        self.assertEqual(len(find), 1)
        self.assertEqual(find[0].id, self.b1_id)
