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
        pass
        #self.connection.drop_database(self.dbname)
