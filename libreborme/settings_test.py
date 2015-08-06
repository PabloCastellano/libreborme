from .settings import *
from mongoengine.connection import connect, disconnect

disconnect()
MONGODB_DATABASES = {
    'default': {'name': 'test_' + MONGO_DATABASE_NAME}
}

MONGODB = connect('test_' + MONGO_DATABASE_NAME)
MONGODB.drop_database('test_' + MONGO_DATABASE_NAME)
