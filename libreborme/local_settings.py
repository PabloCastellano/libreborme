from settings import *


STATICFILES_DIRS = (
    '/home/pablo/src/libreborme/libreborme/static/',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    '/home/pablo/src/libreborme/libreborme/templates/',
    '/home/pablo/src/libreborme/borme/templates/',
)

FIXTURE_DIRS = (
    '/home/pablo/src/libreborme/libreborme/fixtures/',
)

SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'
