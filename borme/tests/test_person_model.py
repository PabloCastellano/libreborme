from django.test import TestCase

from borme.models import Person

import datetime
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)


class TestPersonModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):
        super(TestPersonModel, cls).setUpClass()

        p1 = Person(name='JUAN', date_updated=today)
        p1.save()

    def test_person_object(self):
        find = Person.objects.filter(name='JUAN')
        self.assertEqual(len(find), 1)
        self.assertEqual(find[0].slug, 'juan')
        self.assertEqual(find[0].date_updated, today)

    def test_update_cargos(self):
        p = Person.objects.get(name='JUAN')
        self.assertEqual(p.cargos_actuales, [])
        self.assertEqual(p.cargos_historial, [])

        cargo_entrante = {'title': 't', 'name': 'n', 'date_from': today}

        p.update_cargos_entrantes([cargo_entrante])
        self.assertEqual(p.cargos_actuales, [cargo_entrante])
        self.assertEqual(p.cargos_historial, [])

        cargo_saliente = {'title': 't', 'name': 'n', 'date_to': tomorrow}

        p.update_cargos_salientes([cargo_saliente])
        self.assertEqual(p.cargos_actuales, [])
        self.assertEqual(p.cargos_historial, [{'title': 't', 'name': 'n', 'date_from': today, 'date_to': tomorrow}])
