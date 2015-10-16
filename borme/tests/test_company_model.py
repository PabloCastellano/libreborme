from django.test import TestCase
from borme.models import Company

c1_id = None


class TestCompanyModel(TestCase):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):
        super(TestCompanyModel, cls).setUpClass()

        global c1_id

        # Create two objects for test
        c1 = Company(name='PATATAS JUAN SL')
        c1.save()

        # Save the id of objects to match in the test
        c1_id = c1.id

    @classmethod
    def tearDownClass(cls):
        Company.objects.all().delete()
        super(TestCompanyModel, cls).tearDownClass()

    # This method run on every test
    def setUp(self):
        global c1_id
        self.c1_id = c1_id

    def test_company_object(self):
        find = Company.objects.filter(name='PATATAS JUAN SL')
        self.assertEqual(len(find), 1)
        self.assertEqual(find[0].id, self.c1_id)
        find = Company.objects.filter(slug='patatas-juan-sl')
        self.assertEqual(len(find), 1)
        self.assertEqual(find[0].id, self.c1_id)

"""
def test_company():
    c = Company.objects.get('asdfg SL')
    c.in_bormes == ['1', '2', '3']

def test_person():
    p = Person.objects.get('hjkl')
    p.in_bormes == ['1', '2', '3']

def test_active():
    c = Company.objects.get('asdfg SL')
    c.is_active == False

def test_general():
    Company.objects.count() == 1823
    Person.objects.count() == 23
    Borme.objects.count() == 1233
    Acto.objects.count() == 123385771
"""
