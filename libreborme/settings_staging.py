import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = 'beta.libreborme.net'
ALLOWED_HOSTS = ['localhost', DOMAIN]

SITE_URL = 'http://beta.libreborme.net/'

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
    dsn=os.getenv('RAVEN_DSN'),
    integrations=[DjangoIntegration()]
)


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_ROOT = '/static'

# BORME
BORME_ROOT = '/opt/libreborme/bormes'
BORME_PDF_ROOT = os.path.join(BORME_ROOT, 'pdf')
BORME_XML_ROOT = os.path.join(BORME_ROOT, 'xml')
BORME_JSON_ROOT = os.path.join(BORME_ROOT, 'json')
BORME_LOG_ROOT = os.path.join(BASE_DIR, '..', 'log')

EMAIL_CONTACT = 'contacto@libreborme.net'

# TODO
LOPD = {'provider': 'Some real name',
        'id': 'Some real state issued ID number',
        'domain': 'The domain that hosts this website',
        'email':  EMAIL_CONTACT,
        'address': 'Some real address'}

INTERNAL_IPS.extend(['90.162.50.235', '93.176.138.65'])

EMAIL_HOST = "mailsrv9.dondominio.com"
EMAIL_HOST_USER = "noreply@libreborme.net"
EMAIL_HOST_PASSWORD = 'l$p_bRtWS5(Y'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
