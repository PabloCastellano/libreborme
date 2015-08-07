from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.six import StringIO

from borme.models import Person, Company, Borme, Config
from borme.tests.mongotestcase import MongoFixturesTestCase
from django_mongoengine.tests import MongoTestCase

import os
from datetime import datetime

# parametros django call_command
# what to check django tests
# Envio de emails
# Plantillas
class TestBasicHttp(MongoTestCase):

    # FIXME: Pq si no cargo person.json, los test van bien pero con company.json si fallan?
    """
    mongo_fixtures = {'Anuncio':'anuncio.json', 'Borme': 'borme.json', 'BormeLog': 'borme_log.json',
                      'Company': 'company.json', 'Config': 'config.json', 'Person': 'person.json'}
    """

    @classmethod
    def setUpClass(cls):
        Company(name='EMPRESA RANDOM SL').save()
        Person(name='PERSONA RANDOM').save()
        Config(version='test', last_modified=datetime.now()).save()
        super(TestBasicHttp, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        Company.objects.delete()
        Person.objects.delete()
        Config.objects.delete()
        super(TestBasicHttp, cls).tearDownClass()

    def test_empresa(self):
        company = Company.objects.get(name='EMPRESA RANDOM SL')
        url = reverse('borme-empresa', args=[company.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-empresa', args=['doesnt-exist-sl'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_persona(self):
        person = Person.objects.get(name='PERSONA RANDOM')
        url = reverse('borme-persona', args=[person.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-persona', args=['doesnt-exist'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_index(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/wrongurl/')
        self.assertEqual(response.status_code, 404)

    def test_busqueda(self):
        url = reverse('borme-search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # self.client.post

    def test_empresas(self):
        url = reverse('borme-empresas-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_personas(self):
        url = reverse('borme-personas-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestCommands(MongoTestCase):
    def test_importbormefile(self):
        out = StringIO()
        # FIXME: $HOME
        call_command('importbormefile', os.path.expanduser('~/.bormes/pdf/BORME-A-2015-27-10.pdf'), stdout=out)
        self.assertIn(out.getvalue(), 'Errors: 0')

    def test_importborme(self):
        out = StringIO()
        call_command('importborme', stdout=out)
        self.assertIn(out.getvalue(), 'Errors: 0')