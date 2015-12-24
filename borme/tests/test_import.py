from borme.models import Anuncio, Borme, Company, Person
from borme.importer import import_borme_pdf, _import1
import os

from django.test import TestCase


class TestImport(TestCase):

    def test_import_borme(self):
        import_borme_pdf(os.path.expanduser('~/.bormes/pdf/2015/02/10/BORME-A-2015-27-10.pdf'))
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        self.assertEqual(len(find), 1)
        self.assertEqual(Anuncio.objects.count(), 30)
        # Anuncios desde el 57315 al 57344
        # BORME-A-2015-27-10
        # borme = bormeparser.parse(filename)
        # Testear:
        # results = _import1(borme)
