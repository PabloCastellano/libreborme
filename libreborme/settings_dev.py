import os

from .settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

DOMAIN = 'localhost'
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.ngrok.io']

SITE_URL = 'http://localhost:8000/'

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

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_URL = '%s/media/' % SITE_URL

# BORME
BORME_ROOT = os.path.expanduser('~/.bormes')
BORME_PDF_ROOT = os.path.join(BORME_ROOT, 'pdf')
BORME_XML_ROOT = os.path.join(BORME_ROOT, 'xml')
BORME_JSON_ROOT = os.path.join(BORME_ROOT, 'json')
BORME_LOG_ROOT = os.path.join(BASE_DIR, '..', 'log')

EMAIL_HOST = 'localhost'
EMAIL_HOST_USER = 'root@localhost'
EMAIL_PORT = 1025

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER  # used for error reporting
