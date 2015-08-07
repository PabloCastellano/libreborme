from django.core.management import call_command
from django.test.client import Client
from django.utils.six import StringIO

from borme.models import Person, Company, Borme, Config
from borme.tests.mongotestcase import MongoFixturesTestCase
from django_mongoengine.tests import MongoTestCase

import os


# parametros django call_command
# what to check django tests
# Envio de emails
# Plantillas
# Comandos
class TestHttp1(MongoFixturesTestCase):

    # FIXME: Pq si no cargo person.json, los test van bien pero con company.json si fallan?
    mongo_fixtures = {'Anuncio':'anuncio.json', 'Borme': 'borme.json', 'BormeLog': 'borme_log.json',
                      'Company': 'company.json', 'Config': 'config.json', 'Person': 'person.json'}


    def test_empresa(self):
        company = Company.objects.get(name='ALDARA CATERING SL')
        #company = Company.objects.first()
        #company = Company(name='PATATAS SL')
        #company.save()
        response = self.client.get('/borme/empresa/%s' % company.slug)
        self.assertEqual(response.status_code, 200)

    def test_persona(self):
        person = Person.objects.get(name='PANIAGUA SANCHEZ JOSE ANTONIO')
        #person = Person.objects.first()
        #person = Person(name='JUAN RAMON CORTES')
        #person.save()
        response = self.client.get('/borme/persona/%s' % person.slug)
        self.assertEqual(response.status_code, 200)


class TestHttp2(MongoTestCase):
    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/borme/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/fakeurl/')
        self.assertEqual(response.status_code, 404)

    def test_busqueda(self):
        response = self.client.get('/borme/busqueda/')
        self.assertEqual(response.status_code, 200)
        # self.client.post

    def test_empresas(self):
        response = self.client.get('/borme/empresas/')
        self.assertEqual(response.status_code, 200)

    def test_personas(self):
        response = self.client.get('/borme/personas/')
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