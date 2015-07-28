from .settings import *
from mongoengine.connection import connect, disconnect

disconnect()
MONGODB = connect('test_' + MONGO_DBNAME)
MONGODB.drop_database('test_' + MONGO_DBNAME)
