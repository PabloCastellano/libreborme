from django.conf import settings
import json
import os
import time
import importlib

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
        self.db_name = 'test_libreborme'  # FIXME hardcoded
        self.fixtures_path = 'borme/fixtures'  # FIXME
        super(MongoFixturesTestCase, self).__init__(methodName)

    def _pre_setup(self):
        """
        Load mongo fixtures.
        """
        if self.mongo_fixtures:
            self._load_fixtures(self.mongo_fixtures)
        super(MongoFixturesTestCase, self)._pre_setup()

    def _load_fixtures(self, fixtures):
        """
        Load fixtures from json files.
        Before loading content of every collection
        will be removed.

        :param fixtures:
            dictionary, see :py:attr:`~MongoTestCase.mongo_fixtures`.
        """
        for collname, filename in fixtures.items():
            #print('loading fixture %s' % filename)
            self._import_json(collname, filename)

    def _import_json(self, collname, filename):
        path = '%s/%s' % (self.fixtures_path, filename)
        models = importlib.import_module('borme.models')
        klass = getattr(models, collname)
        klass.objects.delete()

        with open(path) as fileobj:
            docs = json.load(fileobj)
            for doc in docs:
                j = json.dumps(doc)
                obj = klass.from_json(j, created=True)
                obj.save()