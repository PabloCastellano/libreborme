import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from bormeparser.config import CONFIG

from .settings import *

try:
    from .settings_override import *
except ImportError:
    pass

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = 'beta.libreborme.net'
ALLOWED_HOSTS = ['localhost', 'beta.libreborme.net', 'staging.ingress.libreborme.net', 'staging.libreborme.net']

SITE_URL = 'http://staging.ingress.libreborme.net/'

INSTALLED_APPS += [
    'debug_toolbar',
    'elastic_panel',
]

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'elastic_panel.panel.ElasticDebugPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]

# DEBUG_TOOLBAR_CONFIG{'JQUERY_URL': '//ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)


sentry_sdk.init(
    dsn=os.environ['RAVEN_DSN'],
    integrations=[DjangoIntegration()]
)


STATIC_ROOT = '/opt/libreborme/static'
MEDIA_URL = '%s/media/' % SITE_URL

# BORME
BORME_ROOT = "/opt/libreborme/bormes/"
BORME_PDF_ROOT = os.path.join(BORME_ROOT, "pdf")
BORME_XML_ROOT = os.path.join(BORME_ROOT, "xml")
BORME_JSON_ROOT = os.path.join(BORME_ROOT, "json")
BORME_LOG_ROOT = os.path.join(BORME_ROOT, "logs")

EMAIL_CONTACT = 'contacto@libreborme.net'

LOPD = {'provider': 'Pablo Castellano García-Saavedra',
        'id': '76429329F',
        'domain': 'libreborme.net',
        'email':  EMAIL_CONTACT,
        'address': 'Carrer de Morella 47, 12170 - Sant Mateu (Castellón)'}

INTERNAL_IPS.extend(['88.13.29.103'])

EMAIL_HOST = "mailsrv9.dondominio.com"
EMAIL_HOST_USER = "noreply@libreborme.net"
EMAIL_HOST_PASSWORD = 'l$p_bRtWS5(Y'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting

LOGLEVEL = os.environ.get('LOGLEVEL', 'info').upper()
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['require_debug_true'],
            # 'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'errorlogfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BORME_LOG_ROOT, 'libreborme.error.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
        },
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BORME_LOG_ROOT, 'libreborme.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            # 'backupCount': 10,
        },
        'bormelogfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BORME_LOG_ROOT, 'borme.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50MB
            # 'backupCount': 10,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'logfile'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console', 'logfile'],
            'level': 'ERROR',
        },
        # Elasticsearch module is quite noisy
        'elasticsearch': {
            'level': 'WARNING',
            'handlers': ['console'],
            'propagate': False,
        },
        'libreborme': {
            'handlers': ['logfile', 'errorlogfile'],
            'level': LOGLEVEL,
        },
        'borme': {
            'handlers': ['logfile', 'bormelogfile'],
            'level': LOGLEVEL,
        },
        'dataremoval': {
            'handlers': ['logfile', ],
            'level': LOGLEVEL,
        },
    }
}
