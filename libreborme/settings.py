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

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'libreborme.net']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap',
    'django_static_jquery',
    'fontawesome',
    'haystack',
    'tastypie',
    #'maintenancemode',
    'borme',
    'libreborme',
)

if DEBUG:
    INSTALLED_APPS += (
        'django_extensions',
        'debug_toolbar',
    )

if DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

if DEBUG:
    MIDDLEWARE += (
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

# DEBUG
#DEBUG_TOOLBAR_CONFIG{'JQUERY_URL': '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'libreborme',
        'USER': 'libreborme',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# haystack search using elasticsearch
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'borme.search_backends.AsciifoldingElasticSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'libreborme',
    },
}

# http://django-haystack.readthedocs.org/en/latest/signal_processors.html
HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# increase the default number of results (from 20)
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 25

TASTYPIE_DEFAULT_FORMATS = ['json']

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

# Número de elementos a mostrar en las tablas de cargos
CARGOS_LIMIT = 20

# BORME
BORME_ROOT = os.path.expanduser('~/.bormes')
BORME_PDF_ROOT = os.path.join(BORME_ROOT, 'pdf')
BORME_XML_ROOT = os.path.join(BORME_ROOT, 'xml')
BORME_JSON_ROOT = os.path.join(BORME_ROOT, 'json')

BORME_LOG_ROOT = os.path.join(BASE_DIR, '..', 'log')

EMAIL_CONTACT = 'contact@domain'

LOPD = {'provider': 'Some real name',
        'id': 'Some real state issued ID number',
        'domain': 'The domain that hosts this website',
        'email':  EMAIL_CONTACT,
        'address': 'Some real address'}
