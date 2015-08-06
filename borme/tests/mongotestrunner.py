from django.test.runner import DiscoverRunner
from django.conf import settings
from mongoengine.connection import connect, disconnect, get_connection


class MongoTestRunner(DiscoverRunner):
    """
        A test runner that can be used to create, connect to, disconnect from,
        and destroy a mongo test database for standard django testing.

        NOTE:
            The MONGO_PORT and MONGO_DATABASE_NAME settings must exist, create them
            if necessary.

        REFERENCE:
            http://nubits.org/post/django-mongodb-mongoengine-testing-with-custom-test-runner/
    """

    mongodb_name = 'test_%s' % (settings.MONGO_DATABASE_NAME, )

    def setup_databases(self, **kwargs):
        disconnect()
        connect(self.mongodb_name, port=settings.MONGODB_PORT)
        print('Creating mongo test database %s' % self.mongodb_name)

    # Esto destruye la BD al final de los tests, no al final de casa test
    # Falla si ejecuto manage.py test borme.tests libreborme.tests
    def teardown_databases(self, old_config, **kwargs):
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        print('Dropping mongo test database: %s' % self.mongodb_name)
        disconnect()