from borme.models import Borme, Anuncio
from borme.utils import import_borme_file, _import1
#from django.contrib.auth.models import User
#from mongoengine.django.auth import User
import nose.tools as nt
import datetime
import os

from django_mongoengine.tests import MongoTestCase

import bormeparser

b1_id = None


# Hacer Mockup de:
# borme = bormeparser.parse(filename)
# Testear: _import1(borme)
class TestBorme1(MongoTestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):

        global b1_id

        # Create two objects for test
        b1 = Borme(cve='BORME-A-2015-27-10',  date=datetime.date(2015, 2, 10),
                   url='http://boe.es/borme/dias/2015/02/10/pdfs/BORME-A-2015-27-10.pdf',
                   province=bormeparser.PROVINCIA.CACERES.code, section='A')
        b1.save()

        # Save the id of objects to match in the test
        b1_id = b1.id

    # This method run on every test
    def setUp(self):
        global b1_id
        self.b1_id = b1_id
        super(TestBorme1, self).setUp()
        #self.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        #self.user = User.create_user(username='john', email='lennon@thebeatles.com', password='johnpassword')

    def test_borme_object(self):
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        nt.assert_equals(len(find), 1)
        nt.assert_equals(find[0].id, self.b1_id)


class TestBorme2(MongoTestCase):

    def test_import_borme_mongo(self):
        #borme = None
        #results = _import1(borme)
        #FIXME: HOME
        import_borme_file(os.path.expanduser('~/.bormes/pdf/BORME-A-2015-27-10.pdf'))
        find = Borme.objects.filter(cve='BORME-A-2015-27-10')
        nt.assert_equals(len(find), 1)
        borme = find[0]
        nt.assert_equals(Anuncio.objects.count(), 30)
        # Anuncios desde el 57315 al 57344
        #BORME-A-2015-27-10
        # borme = bormeparser.parse(filename)
        # Testear: _import1(borme)


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


"""
from mongoengine import *

connect("libreborme_tests")

def setUp():
    db.import(json1)
    db.import(json2)
    db.import(json3)

def test_company():
    c = Company.objects.get('asdfg')
    c.in_bormes == ['1', '2', '3']

def test_person():
    p = Person.objects.get('hjkl')
    p.in_bormes == ['1', '2', '3']

def test_names_utf8():
    c = Company.objects.get('Valdepeñas')
    p = Person.objects.filter('Gómez')

def test_active():
    c = Company.objects.get('Valdepeñas')
    c.is_active == False

def test_general():
    Company.objects.count() == 1823
    Person.objects.count() == 23
    Borme.objects.count() == 1233
    Acto.objects.count() == 123385771
"""
