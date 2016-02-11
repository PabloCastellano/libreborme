from django.test import TestCase

from borme.models import Company

import datetime
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

class TestCompanyModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):
        super(TestCompanyModel, cls).setUpClass()

        c1 = Company(name='PATATAS JUAN SL', date_updated=today)
        c1.save()

    def test_company_object(self):
        find = Company.objects.filter(name='PATATAS JUAN SL')
        self.assertEqual(len(find), 1)
        self.assertEqual(find[0].slug, 'patatas-juan-sl')
        self.assertEqual(find[0].date_updated, today)

    def test_update_cargos(self):
        c = Company.objects.get(name='PATATAS JUAN SL')
        self.assertEqual(c.cargos_actuales, [])
        self.assertEqual(c.cargos_historial, [])

        cargo_entrante = {'title': 't', 'name': 'n', 'date_from': today, 'type': 'company'}

        c.update_cargos_entrantes([cargo_entrante])
        self.assertEqual(c.cargos_actuales_c, [{'title': 't', 'name': 'n', 'date_from': today}])
        self.assertEqual(c.cargos_actuales_p, [])
        self.assertEqual(c.cargos_historial, [])

        cargo_saliente = {'title': 't', 'name': 'n', 'date_to': tomorrow, 'type': 'company'}

        c.update_cargos_salientes([cargo_saliente])
        self.assertEqual(c.cargos_actuales, [])
        self.assertEqual(c.cargos_historial_p, [])
        self.assertEqual(c.cargos_historial_c, [{'title': 't', 'name': 'n', 'date_from': today, 'date_to': tomorrow}])
