from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.utils.six import StringIO
from django.conf import settings

from borme.models import Anuncio, Borme, Config, Company, Person
from borme.tests.mongotestcase import MongoFixturesTestCase
from django_mongoengine.tests import MongoTestCase

#from django.contrib.auth.models import User
from django.utils import timezone

import os



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
        Config(version='test', last_modified=timezone.now()).save()
        super(TestBasicHttp, cls).setUpClass()

    # This method run on every test
    def setUp(self):
        #self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        #self.user = User.create_user(username='john', email='lennon@thebeatles.com', password='johnpassword')
        super(TestBasicHttp, self).setUp()

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

    @classmethod
    def tearDownClass(cls):
        Anuncio.objects.delete()
        Borme.objects.delete()
        Company.objects.delete()
        Person.objects.delete()
        Config.objects.delete()
        super(TestCommands, cls).tearDownClass()

    def test_importbormepdf(self):
        out = StringIO()
        path = os.path.join(settings.BORME_PDF_ROOT, '2015', '02', '10', 'BORME-A-2015-27-10.pdf')
        call_command('importbormepdf', path, stdout=out)
        self.assertIn(out.getvalue(), 'Errors: 0')

    def test_importbormejson(self):
        pass

    def test_importborme(self):
        out = StringIO()
        call_command('importborme', stdout=out)
        self.assertIn(out.getvalue(), 'Errors: 0')

"""

    def test_login_required(self):
        response = self.client.get(reverse('process_all'))
        self.assertRedirects(response, '/login')

    def test_get_method(self):
        self.client.login(username='john', password='johnpassword')
        response = self.client.get(reverse('process_all'))
        self.assertRedirects(response, '/reports/messages')

        # assert no messages were sent

    def test_post_method(self):
        self.client.login(username='john', password='johnpassword')

        # add pending messages, mock sms sending?

        response = self.client.post(reverse('process_all'))
        self.assertRedirects(response, '/reports/messages')

        # assert that sms messages were sent
"""
