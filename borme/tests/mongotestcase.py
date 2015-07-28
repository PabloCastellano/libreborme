from django.conf import settings
import json
from subprocess import call
import os
import time


class MongoTestCase(object):
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
