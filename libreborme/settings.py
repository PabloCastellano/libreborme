"""
Django settings for libreborme project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from os import environ, path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = path.dirname(path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = environ.get('SECRET_KEY', '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = environ.get("DEBUG", "True").upper() == "TRUE"

ALLOWED_HOSTS = environ.get("ALLOWED_HOSTS", "127.0.0.1, libreborme.net, librebor.me").split(",")

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.staticfiles',

    'health_check',
    'health_check.db',

    'bootstrap',
    'django_static_jquery',
    'fontawesome',
    'tastypie',
    # 'maintenancemode',
    'django_elasticsearch_dsl',
    'borme',
    'libreborme',
)


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)


# if DEBUG:
#     INSTALLED_APPS += (
#         'django_extensions',
#         'debug_toolbar',
#         'elastic_panel',
#     )
#
#     DEBUG_TOOLBAR_PANELS = [
#         'debug_toolbar.panels.versions.VersionsPanel',
#         'debug_toolbar.panels.timer.TimerPanel',
#         'debug_toolbar.panels.settings.SettingsPanel',
#         'debug_toolbar.panels.headers.HeadersPanel',
#         'debug_toolbar.panels.request.RequestPanel',
#         'debug_toolbar.panels.sql.SQLPanel',
#         'elastic_panel.panel.ElasticDebugPanel',
#         'debug_toolbar.panels.staticfiles.StaticFilesPanel',
#         'debug_toolbar.panels.templates.TemplatesPanel',
#         'debug_toolbar.panels.cache.CachePanel',
#         'debug_toolbar.panels.signals.SignalsPanel',
#         'debug_toolbar.panels.logging.LoggingPanel',
#         'debug_toolbar.panels.redirects.RedirectsPanel',
#     ]
#
#     CACHES = {
#         'default': {
#             'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#         }
#     }
#
#     MIDDLEWARE += (
#         'debug_toolbar.middleware.DebugToolbarMiddleware',
#     )


ROOT_URLCONF = environ.get("ROOT_URLCONF", "libreborme.urls")

TEMPLATES = [
    {
        "BACKEND": environ.get("TEMPLATES_BACKEND", "django.template.backends.django.DjangoTemplates"),
        "DIRS": [dir for dir in environ.get("TEMPLATES_DIRS", "").split(",") if dir],
        "APP_DIRS": environ.get("TEMPLATES_APP_DIRS", "True").upper() == "TRUE",
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'libreborme.context_processors.piwik',
                'libreborme.context_processors.common',
            ],
        },
    },
]

WSGI_APPLICATION = environ.get("WSGI_APPLICATION", "libreborme.wsgi.application")

# DEBUG
# DEBUG_TOOLBAR_CONFIG{'JQUERY_URL': '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'}

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        "ENGINE": environ.get("DATABASES_DEFAULT_ENGINE", "django.db.backends.postgresql_psycopg2"),
        "NAME": environ.get("DATABASES_DEFAULT_NAME", "libreborme"),
        "USER": environ.get("DATABASES_DEFAULT_USER", "libreborme"),
        "PASSWORD": environ.get("DATABASES_DEFAULT_PASSWORD", "password"),
        "HOST": environ.get("DATABASES_DEFAULT_HOST", "localhost"),
        "PORT": environ.get("DATABASES_DEFAULT_PORT", ""),
    }
}

ELASTICSEARCH_URI = environ.get("ELASTICSEARCH_URI", "http://elastic:changeme@localhost:9200")
ELASTICSEARCH_DSL = {
    'default': {
        "hosts": environ.get("ELASTICSEARCH_DSL_DEFAULT_HOSTS", ELASTICSEARCH_URI.split('http://')[1])
    },
}

# ELASTICSEARCH_DSL_AUTOSYNC = False
# ELASTICSEARCH_DSL_AUTO_REFRESH = False

TASTYPIE_DEFAULT_FORMATS = environ.get("TASTYPIE_DEFAULT_FORMATS", "json").split(",")

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = environ.get("LANGUAGE_CODE", "es")

TIME_ZONE = environ.get("TIME_ZONE", "Europe/Madrid")

USE_I18N = environ.get("USE_I18N", "True").upper() == "TRUE"

USE_L10N = environ.get("USE_L10N", "True").upper() == "TRUE"

USE_TZ = environ.get("USE_TZ", "True").upper() == "TRUE"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = environ.get("STATIC_URL", "/static/")

PIWIK_URL = environ.get("PIWIK_URL", "")
PIWIK_SITE_ID = environ.get("PIWIK_SITE_ID", "")

# Número de elementos a mostrar en las tablas de cargos
CARGOS_LIMIT = int(environ.get("CARGOS_LIMIT", "20"))

# BORME
BORME_ROOT = environ.get("BORME_ROOT", path.expanduser('~/.bormes'))
BORME_PDF_ROOT = environ.get("BORME_PDF_ROOT", path.join(BORME_ROOT, 'pdf'))
BORME_XML_ROOT = environ.get("BORME_XML_ROOT", path.join(BORME_ROOT, 'xml'))
BORME_JSON_ROOT = environ.get("BORME_JSON_ROOT", path.join(BORME_ROOT, 'json'))

STATIC_ROOT = environ.get("STATIC_ROOT", "/app/libreborme/static")

BORME_LOG_ROOT = environ.get("BORME_LOG_ROOT", path.join(BASE_DIR, '..', 'log'))

EMAIL_CONTACT = environ.get("EMAIL_CONTACT", "contact@domain")

LOPD = {
    "provider": environ.get("LOPD_PROVIDER", "Some real name"),
    "id": environ.get("LOPD_ID", "Some real state issued ID number"),
    "domain": environ.get("LOPD_DOMAIN", "The domain that hosts this website"),
    "email": environ.get("LOPD_EMAIL", EMAIL_CONTACT),
    "address": environ.get("LOPD_ADDRESS", "Some real address"),
}

HOST_BUCKET = environ.get("HOST_BUCKET", "https://libreborme-prod.ams3.digitaloceanspaces.com")

INTERNAL_IPS = environ.get("INTERNAL_IPS", "127.0.0.1").split(",")
LOGIN_URL = environ.get("LOGIN_URL", "/admin/login/")
