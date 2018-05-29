from django.core.management import call_command
from django.urls import reverse
from django.test.client import Client
from django.utils.six import StringIO
from django.conf import settings

from borme.models import Anuncio, Borme, Config, Company, Person
from django.test import TestCase

#from django.contrib.auth.models import User
from django.utils import timezone

import datetime
today = datetime.date.today()

import os


# TODO: Fixtures
# parametros django call_command
# what to check django tests
# Envio de emails
# Plantillas
class TestBasicHttp(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestBasicHttp, cls).setUpClass()
        b = Borme.objects.create(cve='BORME-Z-1111', date=today, url='http://localhost', from_reg=1, until_reg=10, province='Nowhere', section='A')
        c = Company(name='EMPRESA RANDOM', type='SL', date_updated=today)
        c.save()
        Person.objects.create(name='PERSONA RANDOM', date_updated=today)
        a = Anuncio.objects.create(id_anuncio=1, year=1800, borme=b, company=c)
        c.anuncios = [{"year": 1800, "id": a.id}]
        c.save()
        Config.objects.create(version='test', last_modified=timezone.now())
        #self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        #self.user = User.create_user(username='john', email='lennon@thebeatles.com', password='johnpassword')

    def test_empresa(self):
        company = Company.objects.get(name='EMPRESA RANDOM')
        url = reverse('borme-empresa', args=[company.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-empresa', args=['doesnt-exist'])
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

    def test_anuncio(self):
        anuncio = Anuncio.objects.get(id_anuncio=1, year=1800)
        url = reverse('borme-anuncio', args=[anuncio.year, anuncio.id_anuncio])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-anuncio', args=[1700, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_borme(self):
        borme = Borme.objects.get(cve='BORME-Z-1111')
        url = reverse('borme-borme', args=[borme.cve])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('borme-borme', args=['BORME-Z-DOESNTEXIST'])
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

    """
    TODO:

    'borme-provincia'
    'borme-provincia-fecha'
    'borme-fecha'
    'borme-empresa-csv-actual'
    'borme-empresa-csv-historial'
    'borme-persona-csv-actual'
    'borme-persona-csv-historial'
    API
    """


"""
class TestCommands(TestCase):

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
