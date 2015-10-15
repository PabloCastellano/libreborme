"""
Django settings for libreborme project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from mongoengine.connection import connect, disconnect

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #mongoengine.django.mongo_auth,
    'bootstrap',
    'borme',
    'libreborme',
    'mongogeneric',
    'mongodbforms',
)

if DEBUG:
    INSTALLED_APPS += (
        'django_extensions',
        'debug_toolbar',
        'mongonaut',
#        'django_nose',
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

if DEBUG:
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

ROOT_URLCONF = 'libreborme.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.contrib.auth.context_processors.auth',
                'libreborme.context_processors.piwik',
                'libreborme.context_processors.common',
            ],
        },
    },
]

WSGI_APPLICATION = 'libreborme.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

"""
DATABASES = {
    'default': {'ENGINE': 'django.db.backends.dummy'}
}
"""

# No se usan pero se necesitan para que los tests no se quejen por usar
# TestCase y tener una implementación de MongoTestCase incompleta.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# MongoDB Databases
MONGODB_DATABASES = {
    'default': {'name': 'libreborme'}
}

MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
MONGO_DATABASE_NAME = 'libreborme'
connect(MONGO_DATABASE_NAME)

AUTHENTICATION_BACKENDS = (
    'django_mongoengine.auth.backends.MongoEngineBackend',
)

SESSION_ENGINE = 'django_mongoengine.sessions'
MONGOENGINE_USER_DOCUMENT = 'django_mongoengine.auth.models.User'

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'es'

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

PIWIK_URL = ''
PIWIK_SITE_ID = ''

TEST_RUNNER = 'borme.tests.mongotestrunner.MongoTestRunner'

# BORME
BORME_ROOT = os.path.expanduser('~/.bormes')
BORME_PDF_ROOT = os.path.join(BORME_ROOT, 'pdf')
BORME_XML_ROOT = os.path.join(BORME_ROOT, 'xml')
BORME_JSON_ROOT = os.path.join(BORME_ROOT, 'json')

BORME_LOG_ROOT = os.path.join(SITE_ROOT, '..', 'log')
