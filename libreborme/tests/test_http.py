from django.core.management import call_command
from django.test.client import Client
from django.utils.six import StringIO

from borme.models import Person, Company, Borme, Config

import nose.tools as nt
import os

from borme.tests.mongotestcase import MongoTestCase


# parametros django call_command
# what to check django tests
# Envio de emails
# Plantillas
# Comandos
class TestHttp(MongoTestCase):
    fixtures = ['anuncio.json', 'borme.json', 'borme_log.json', 'company.json', 'config.json', 'person.json', 'jfaosfjasf']
    #fixtures = ['anuncio.json', 'borme.json', 'borme_log.json', 'company.json', 'config.json']

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
        company = Company.objects.first()
        response = self.client.get('/borme/empresa/%s' % company.slug)
        nt.assert_equals(response.status_code, 200)

    def test_personas(self):
        response = self.client.get('/borme/personas/')
        nt.assert_equals(response.status_code, 200)

    def test_persona(self):
        person = Person.objects.first()
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
