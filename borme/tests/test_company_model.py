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
        company = Company.objects.filter(name='PATATAS JUAN SL')
        self.assertEqual(len(company), 1)
        company = company[0]
        self.assertEqual(company.slug, 'patatas-juan')
        self.assertEqual(company.date_updated, today)

    def test_update_cargos(self):
        c = Company.objects.get(name='PATATAS JUAN SL')
        self.assertEqual(c.get_cargos_actuales()[0], [])
        self.assertEqual(c.get_cargos_historial()[0], [])

        cargo_entrante = {
            'title': 't',
            'name': 'n',
            'date_from': today,
            'type': 'company'
        }

        c.update_cargos_entrantes([cargo_entrante])
        self.assertEqual(c.cargos_actuales_c,
                         [{'title': 't', 'name': 'n', 'date_from': today}])
        self.assertEqual(c.cargos_actuales_p, [])
        self.assertEqual(c.get_cargos_historial()[0], [])

        cargo_saliente = {
            'title': 't',
            'name': 'n',
            'date_to': tomorrow,
            'type': 'company'
        }

        c.update_cargos_salientes([cargo_saliente])
        self.assertEqual(c.get_cargos_actuales()[0], [])
        self.assertEqual(c.cargos_historial_p, [])

        cargos_salientes = [{
            'title': 't',
            'name': 'n',
            'date_from': today,
            'date_to': tomorrow
        }]
        self.assertEqual(
            c.cargos_historial_c,
            cargos_salientes
        )
