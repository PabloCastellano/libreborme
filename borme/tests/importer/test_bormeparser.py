from borme.models import Anuncio, Borme, BormeLog, Company, Person
import borme.parser.importer
import borme.parser.logger
import borme.utils.strings

import datetime
import gzip
import logging
import os

from django.test import TestCase
from django.test.utils import override_settings

THIS_PATH = os.path.dirname(os.path.abspath(__file__))
FILES_PATH = os.path.join(THIS_PATH, '../files')

# Disable loggers
borme.utils.strings.logger.setLevel(logging.ERROR)
borme.parser.importer.logger.setLevel(logging.ERROR)
borme.parser.logger.logger.setLevel(logging.ERROR)


@override_settings(PARSER='borme.parser.backend.bormeparser')
def load_borme_from_gzipped_json(filename):
    fp = gzip.open(os.path.join(FILES_PATH, 'bormeparser', filename))
    ret = borme.parser.importer.from_json_file(fp)
    fp.close()
    return ret


# TODO: Use a lighter one, this BORME takes too long for a simple test (several minutes)
class TestImportAnuncios_BORME_A_2012_197_28(TestCase):

    def test_nombramientos_ceses(self):
        """Importa un BORME-JSON con Nombramientos y otro posteriormente
           con Ceses, y comprueba que cada cargo se ha contabilizado
           correctamente
        """
        companies = Company.objects.all()
        self.assertEqual(len(companies), 0)

        ret = load_borme_from_gzipped_json("BORME-A-2009-197-28.json.gz")
        self.assertTrue(ret)
        self.assertEqual(Company.objects.count(), 290)
        self.assertEqual(Person.objects.count(), 399)
        self.assertEqual(Borme.objects.count(), 1)
        self.assertEqual(BormeLog.objects.count(), 1)

        company = Company.objects.get(slug='labiernag-2000')
        self.assertEqual(len(company.get_cargos_actuales()[0]), 6)
        self.assertEqual(len(company.get_cargos_historial()[0]), 0)
        self.assertEqual(len(company.auditors), 1)

        # Acto: Constitución
        company = Company.objects.get(slug='locutorio-mafer-2009')
        self.assertEqual(company.date_creation, datetime.date(2009, 9, 30))

        # Acto: "Disolución"
        company = Company.objects.get(slug='latinif-iberica-servicios-comerciales-itfrespor')
        self.assertEqual(company.status, "dissolved")
        self.assertEqual(len(company.liquidators), 2)
        self.assertEqual(company.reason_dissolution, "Voluntaria.")

        # Acto: Cambio de domicilio social
        company = Company.objects.get(slug='cifialdecor')
        self.assertEqual(company.type, "SA")
        self.assertEqual(company.domicilio, "C/ URANIO 3 - POLIGONO INDUSTRIAL SAN JOSE DE VALD (LEGANES).")

        # Acto: Cambio de objeto social
        company = Company.objects.get(slug='defcon-technologies')
        self.assertEqual(company.type, "SL")
        self.assertEqual(company.objeto, "EL ASESORAMIENTO Y LA CONSULTORIA, IMPORTACION, EXPORTACION, DISTRIBUCIONE INSTALACION DE SISTEMAS FISICOS Y ELECTRONICOS DE SEGURIDAD Y SUS NECESARIAS INFRAESTRUCTURAS.")

        # Acto: "Disolución" y "Extinción"
        company = Company.objects.get(slug='modas-venus')
        self.assertEqual(company.status, "inactive")
        self.assertEqual(len(company.liquidators), 2)

        ret = load_borme_from_gzipped_json("BORME-A-2012-246-28.json.gz")
        self.assertTrue(ret)
        self.assertEqual(Company.objects.count(), 847)
        company2 = Company.objects.get(slug='labiernag-2000')
        self.assertEqual(len(company2.get_cargos_actuales()[0]), 8)
        self.assertEqual(len(company2.get_cargos_historial()[0]), 3)
        self.assertEqual(len(company2.auditors), 1)


class TestImportAnuncios_BORME_A_2012_246_28(TestCase):

    def setUp(self):
        load_borme_from_gzipped_json("BORME-A-2012-246-28.json.gz")

    def test_total_companies(self):
        self.assertEqual(Company.objects.count(), 563)

    def test_nombramientos_ceses(self):
        """Importa un BORME-JSON y comprueba que un anuncio con Cese y
           Nombramiento de la misma persona es procesado correctamente
           (primero Ceses y luego Nombramientos)
        """
        company = Company.objects.get(slug='ferreteria-viena')
        self.assertEqual(company.name, 'FERRETERIA VIENA SL')
        self.assertEqual(company.fullname, 'Ferreteria Viena SL')
        self.assertEqual(len(company.get_cargos_actuales()[0]), 2)
        self.assertEqual(len(company.get_cargos_historial()[0]), 2)
        self.assertEqual(company.date_updated, datetime.date(2012, 12, 18))

    def test_extincion(self):
        # Acto: "Extinción"
        company = Company.objects.get(slug='pulso-2000')
        self.assertEqual(company.is_active, False)
        self.assertEqual(company.status, 'inactive')
        self.assertEqual(company.date_extinction, datetime.date(2012, 12, 14))


# TODO: Buscar un BORME que tenga los siguientes actos:
# "Reapertura hoja registral"
# "Articulo 378.5 del Reglamento del Registro Mercantil"
# Cierre de hoja registral...
"""
class TestImportAnuncios_BORME_A_2018_51_41(TestCase):
    def setUp(self):
        load_borme_from_gzipped_json("BORME-A-2018-51-41.json.gz")

    def test_total_companies(self):
        self.assertEqual(Company.objects.count(), 102)

    def test_reactive_company(self):
        # Acto: "Reapertura hoja registral"
        company = Company.objects.get(slug='hermanos-caro-monclova')
        self.assertEqual(company.is_active, True)
        self.assertEqual(company.status, 'active')
        self.assertEqual(company.date_extinction, None)

        # Acto: "Articulo 378.5 del Reglamento del Registro Mercantil"
        company = Company.objects.get(slug='agroecija')
        self.assertEqual(company.is_active, True)
        self.assertEqual(company.status, 'active')
        self.assertEqual(company.date_extinction, datetime.date(2018, 3, 13))

    # Cierre hoja de hoja registral
    # self.assertEqual(company.status, 'suspended')
"""
