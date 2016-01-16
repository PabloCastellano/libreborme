from borme.models import Anuncio, Borme, Company
from borme.importer import import_borme_pdf, import_borme_json
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


class TestImport2(TestCase):

    def test_nombramientos_ceses(self):
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        json_path = os.path.join(os.getcwd(), 'borme', 'tests', 'files', '1_nombramientos.json')
        ret = import_borme_json(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(len(company.cargos_actuales), 2)
        self.assertEqual(len(company.cargos_historial), 0)

        json_path = os.path.join(os.getcwd(), 'borme', 'tests', 'files', '2_ceses.json')
        ret = import_borme_json(json_path)
        self.assertTrue(ret)
        companies = Company.objects.all()
        self.assertEqual(len(companies), 1)
        company = companies[0]
        self.assertEqual(len(company.cargos_actuales), 0)
        self.assertEqual(len(company.cargos_historial), 2)
