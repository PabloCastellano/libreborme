import os
import sys
from datetime import timedelta
from django.conf import settings

DEBUG = settings.DEBUG
SERVE_STATIC = DEBUG
TEMPLATE_DEBUG = DEBUG

USE_I18N = True

USE_L10N = True

USE_TZ = True

PROTOCOL = 'http' if DEBUG else 'https'
PORT = getattr(settings, 'PORT', '8000') if DEBUG else None

if PORT and str(PORT) not in ['80', '443']:
    PORT_STRING = ':%s' % PORT
else:
    PORT_STRING = ''

SUBDIR = getattr(settings, 'SUBDIR', '')

if SUBDIR and not SUBDIR.startswith('/'):
    SUBDIR = '/%s' % SUBDIR
elif SUBDIR and SUBDIR.endswith('/'):
    SUBDIR = SUBDIR[0:-1]

SITE_URL = '%s://%s%s%s' % (PROTOCOL, settings.DOMAIN, PORT_STRING, SUBDIR)
SITE_NAME = getattr(settings, 'SITE_NAME', 'Nodeshot')

MEDIA_ROOT = '%s/media/' % settings.SITE_ROOT

MEDIA_URL = '%s/media/' % SITE_URL

STATIC_ROOT = '%s/static/' % settings.SITE_ROOT

STATIC_URL = '%s/static/' % SITE_URL

ALLOWED_HOSTS = ['*']

if PROTOCOL == 'https':
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    os.environ['HTTPS'] = 'on'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
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

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    "django.core.context_processors.debug",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages"
    'libreborme.context_processors.piwik',
    'libreborme.context_processors.common',
)

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
    )

#AUTH_USER_MODEL = 'profiles.Profile'


# ------ FILEBROWSER ------ #

"""
FILEBROWSER_DIRECTORY = ''
"""

# ------ DJANGO CACHE ------ #

"""
CACHES = {
    'rosetta': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'rosetta'
    }
}

if DEBUG:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
else:
    CACHES['default'] = {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': '127.0.0.1:6379:1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }

    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
"""

# ------ EMAIL SETTINGS ------ #

EMAIL_PORT = 1025 if DEBUG else 25  # 1025 if you are in development mode, while 25 is usually the production port

# ------ LOGGING ------ #

# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '\n\n[%(levelname)s %(asctime)s] module: %(module)s, process: %(process)d, thread: %(thread)d\n%(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'logfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': settings.SITE_ROOT + "/../log/libreborme.error.log",
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 3,
            'formatter': 'verbose'
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
            'handlers': ['logfile'],
            'level': 'ERROR',
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        }
    }
}

# ------ CELERY ------ #
"""
if DEBUG:
    # this app makes it possible to use django as a queue system for celery
    # so you don't need to install RabbitQM or Redis
    # pretty cool for development, but might not suffice for production if your system is heavily used
    # our suggestion is to switch only if you start experiencing issues
    INSTALLED_APPS.append('kombu.transport.django')
    BROKER_URL = 'django://'
    # synchronous behaviour for development
    # more info here: http://docs.celeryproject.org/en/latest/configuration.html#celery-always-eager
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
else:
    # in production the default background queue manager is Redis
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    BROKER_TRANSPORT_OPTIONS = {
        "visibility_timeout": 3600,  # 1 hour
        "fanout_prefix": True
    }
    # in production emails are sent in the background
    EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERYBEAT_SCHEDULE = {
    'purge_notifications': {
        'task': 'nodeshot.community.notifications.tasks.purge_notifications',
        'schedule': timedelta(days=1),
    }
}
"""

# ------ DEBUG TOOLBAR ------ #

INTERNAL_IPS = ('127.0.0.1', '::1',)  # ip addresses where you want to show the debug toolbar here
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

# ------ UNIT TESTING SPEED UP ------ #

if 'test' in sys.argv:
    CELERY_ALWAYS_EAGER = True

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
    )
