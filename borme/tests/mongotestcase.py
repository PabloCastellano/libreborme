from django.conf import settings
import json
from subprocess import call
import os
import time

from django_mongoengine.tests import MongoTestCase


#TODO: SimpleMongoTestCase

# https://github.com/hmarr/mongoengine/pull/493/files
class MongoFixturesTestCase(MongoTestCase):
    mongo_fixtures = {}
    """
    Dictionary of fixtures, where each key is a collection name,
    and each value is a name of a json file. Such file contains list
    of documents to load.
    """

    def __init__(self, methodName='runtest'):
        print('222222222222222 init')
        self.db_name = 'test_libreborme'  # FIXME hardcoded
        self.fixtures_path = 'borme/fixtures'  # FIXME
        super(MongoFixturesTestCase, self).__init__(methodName)

    def _pre_setup(self):
        """
        Load mongo fixtures.
        """
        print('22222222222222 _pre_setup')
        if self.mongo_fixtures:
            self._load_fixtures(self.mongo_fixtures)
        super(MongoFixturesTestCase, self)._pre_setup()

    def _load_fixtures(self, fixtures):
        """
        Load fixtures from json files.
        Before loading content of every collection
        will be removed.

        :param fixtures:
            dictionary, seimport pdb
        pdb.set_trace()e :py:attr:`~MongoTestCase.mongo_fixtures`.
        """
        print('22222222222222 _load_fixtures')
        for collname, filename in fixtures.items():
            print('loading fixture %s' % filename)
            collection = self.conn[self.db_name][collname]
            collection.remove()
            path = '%s/%s' %(self.fixtures_path, filename)
            #_import_json1(collection, path)
            _import_json2(self.db_name, collname, path)


# No va pq contiene $oid como atributo empezando por $
def _import_json1(collection, path):
    with open(path) as fileobj:
        docs = json.loads(fileobj.read())
        import pdb
        pdb.set_trace()
        #collection.save(docs)
        for doc in docs:
            collection.save(doc)


# TODO: esconder output
def _import_json2(dbname, collection_name, path):
    call(["mongoimport", "--db", dbname, "--collection", collection_name, "--jsonArray", "--file", path])


class MongoTestCaseOld(object):
    #fixtures = ['anuncio.json', 'borme.json', 'borme_log.json', 'company.json', 'config.json', 'person.json', 'jfaosfjasf']
    fixtures = ['anuncio.json', 'borme.json', 'borme_log.json', 'company.json', 'config.json', 'person.json']

    def setUp(self):
        self.dbname = 'test_' + settings.MONGO_DBNAME
        self.connection = settings.MONGODB
        self.db = self.connection[self.dbname]

        # http://stackoverflow.com/questions/11568246/loading-several-text-files-into-mongodb-using-pymongo
        for fixture in self.fixtures:
            path = 'borme/fixtures/%s' % fixture
            if not os.path.isfile(path):
                raise IOError
            collection_name = fixture.split('.')[0]
            # mongoimport --db libreborme --collection config --file fixture1.json
            time.sleep(2)
            import pdb
            pdb.set_trace()
            call(["mongoimport", "-db %s" % self.dbname, "--collection %s" % collection_name, "--file %s" % path])
            # Popen(['/bin/sh', '-c', args[0], args[1], ...])
            #collection = self.db.create_collection(collection_name)
            #d = json.load(open(fixture))
            #collection.insert(d)


    def tearDown(self):
        pass
        #self.connection.drop_database(self.dbname)
