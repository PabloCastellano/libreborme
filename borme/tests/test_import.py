from borme.models import Anuncio, Borme, Company, Person
from borme.utils import import_borme_pdf, _import1
import os

from django_mongoengine.tests import MongoTestCase


class TestImport(MongoTestCase):

    @classmethod
    def tearDownClass(cls):
        Anuncio.objects.delete()
        Borme.objects.delete()
        Company.objects.delete()
        Person.objects.delete()
        super(TestImport, cls).tearDownClass()

    def test_import_borme_mongo(self):
        #FIXME: HOME
        import_borme_pdf(os.path.expanduser('~/.bormes/pdf/BORME-A-2015-27-10.pdf'))
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        self.assertEqual(len(find), 1)
        self.assertEqual(Anuncio.objects.count(), 30)
        # Anuncios desde el 57315 al 57344
        # BORME-A-2015-27-10
        # borme = bormeparser.parse(filename)
        # Testear:
        # results = _import1(borme)
