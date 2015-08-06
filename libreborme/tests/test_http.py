from django.core.management import call_command
from django.test.client import Client
from django.utils.six import StringIO

from borme.models import Person, Company, Borme, Config
from borme.tests.mongotestcase import MongoFixturesTestCase

import nose.tools as nt
import os


# parametros django call_command
# what to check django tests
# Envio de emails
# Plantillas
# Comandos
class TestHttp(MongoFixturesTestCase):

    # FIXME: Pq si no cargo person.json, los test van bien pero con company.json si fallan?
    mongo_fixtures = {'anuncio':'anuncio.json', 'borme': 'borme.json', 'borme_log': 'borme_log.json',
                      'company': 'company.json', 'config': 'config.json', 'person': 'person.json'}

    def setUp(self):
        self.client = Client()
        config = Config(version='tests')
        config.save()

    def test_index(self):
        response = self.client.get('/')
        nt.assert_equals(response.status_code, 200)
        response = self.client.get('/robots.txt')
        nt.assert_equals(response.status_code, 200)
        response = self.client.get('/borme/')
        nt.assert_equals(response.status_code, 200)
        response = self.client.get('/fakeurl/')
        nt.assert_equals(response.status_code, 404)

    def test_busqueda(self):
        response = self.client.get('/borme/busqueda/')
        nt.assert_equals(response.status_code, 200)
        # self.client.post

    def test_empresas(self):
        response = self.client.get('/borme/empresas/')
        nt.assert_equals(response.status_code, 200)

    def test_empresa(self):
        company = Company.objects.get(name='ALDARA CATERING SL')
        #company = Company.objects.first()
        #company = Company(name='PATATAS SL')
        #company.save()
        response = self.client.get('/borme/empresa/%s' % company.slug)
        nt.assert_equals(response.status_code, 200)

    def test_personas(self):
        response = self.client.get('/borme/personas/')
        nt.assert_equals(response.status_code, 200)

    def test_persona(self):
        person = Person.objects.get(name='PANIAGUA SANCHEZ JOSE ANTONIO')
        #person = Person.objects.first()
        #person = Person(name='JUAN RAMON CORTES')
        #person.save()
        response = self.client.get('/borme/persona/%s' % person.slug)
        nt.assert_equals(response.status_code, 200)

    def test_importbormefile(self):
        out = StringIO()
        # FIXME: $HOME
        call_command('importbormefile', os.path.expanduser('~/.bormes/pdf/BORME-A-2015-27-10.pdf'), stdout=out)
        nt.assert_in(out.getvalue(), 'Errors: 0')

    def test_importborme(self):
        out = StringIO()
        call_command('importborme', stdout=out)
        nt.assert_in(out.getvalue(), 'Errors: 0')
