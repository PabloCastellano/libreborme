from borme.models import Company
import nose.tools as nt


c1_id = None

from django.conf import settings

class MongoTestCase(object):
    fixtures = ['test_data.json']

    def setUp(self):
        self.dbname = 'test_' + settings.MONGO_DBNAME
        self.connection = settings.MONGODB
        self.db = self.connection[self.dbname]
        # TODO: Cargar fixtures
        # http://stackoverflow.com/questions/11568246/loading-several-text-files-into-mongodb-using-pymongo

    def tearDown(self):
        self.db.drop_collection('company')



class TestModelOne(MongoTestCase):

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
        super(TestModelOne, self).setUp()

    def test_company_object(self):
        find = Company.objects.filter(name='PATATAS JUAN SL')
        nt.assert_equals(len(find), 1)
        nt.assert_equals(find[0].id, self.c1_id)
        find = Company.objects.filter(slug='patatas-juan-sl')
        nt.assert_equals(len(find), 1)
        nt.assert_equals(find[0].id, self.c1_id)
