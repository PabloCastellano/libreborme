from borme.models import Company
import nose.tools as nt


# WORKAROUND: https://github.com/mbanton/nose-mongoengine/issues/4
from mongoengine.connection import connect, disconnect
disconnect()
db = connect('asdfg')
db.drop_database('asdfg')

c1_id = None


class TestModelOne(object):

    # This method run on instance of class
    @classmethod
    def setUpClass(cls):

        global c1_id

        # Create two objects for test
        c1 = Company(name='PATATAS JUAN SL')
        c1.save()

        # Save the id of objects to match in the test
        c1_id = c1.id

    # This method run on every test
    def setUp(self):
        global c1_id
        self.c1_id = c1_id

    def test_company_object(self):
        find = Company.objects.filter(name='PATATAS JUAN SL')
        nt.assert_equals(len(find), 1)
        nt.assert_equals(find[0].id, self.c1_id)
        find = Company.objects.filter(slug='patatas-juan-sl')
        nt.assert_equals(len(find), 1)
        nt.assert_equals(find[0].id, self.c1_id)
