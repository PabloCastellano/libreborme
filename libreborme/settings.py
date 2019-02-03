# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '41+h()yq5-!*=)sh+_%4wal8=+*e)dlrau*81odpu7n&9^7d5h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_NAME = 'LibreBORME'
ALLOWED_HOSTS = ['libreborme.net']

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
]

EXTERNAL_APPS = [
    'django_static_jquery',
    'tastypie',
    'maintenance_mode',
    'django_elasticsearch_dsl',
    'bootstrap',
    'fontawesome',
    'bootstrapform',
    'djstripe',
    'prettyjson',
    'django_extensions',
    'compressor',
]

SITE_APPS = [
    'borme',
    'libreborme',
    'alertas',
    'dataremoval',
]

# Application definition
INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + SITE_APPS

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'maintenance_mode.middleware.MaintenanceModeMiddleware',
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    # 'sass_processor.finders.CssFinder',
]

COMPRESS_PRECOMPILERS = (
	('text/x-scss', 'django_libsass.SassCompiler'),
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
                'libreborme.context_processors.piwik',
                'libreborme.context_processors.common',
            ],
        },
    },
]

WSGI_APPLICATION = 'libreborme.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME', 'libreborme'),
        'USER': os.getenv('DB_USER', 'libreborme'),
        'PASSWORD': os.getenv('DB_PASS', 'password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', ''),
    }
}

ELASTICSEARCH_URI = os.getenv('ELASTICSEARCH_URI',
                              "http://elastic:changeme@localhost:9200")
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_URI.split('http://')[1]
    },
}

# ELASTICSEARCH_DSL_AUTOSYNC = False
# ELASTICSEARCH_DSL_AUTO_REFRESH = False

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

# Piwik
PIWIK_URL = os.getenv('PIWIK_URL', '')
PIWIK_SITE_ID = os.getenv('PIWIK_SITE_ID', '')

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

HOST_BUCKET = "https://libreborme-prod.ams3.digitaloceanspaces.com"

ADMINS = (
    ('Pablo', 'pablo@anche.no'),
    ('Libreborme', 'libreborme@libreborme.net'))
MANAGERS = ADMINS

INTERNAL_IPS = ['127.0.0.1']
LOGIN_URL = '/admin/login/'


LOGIN_REDIRECT_URL = '/alertas/'
LOGOUT_REDIRECT_URL = '/borme/'

# stripe
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_SECRET_KEY", "pk_test_0N38FeA9mW1so4zKyCyzcxIE")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_eVEoxiTuoWOlSw104llgXvcs")

# dj-stripe
STRIPE_LIVE_PUBLIC_KEY = os.environ.get("STRIPE_LIVE_PUBLIC_KEY", "xxxx")
STRIPE_LIVE_SECRET_KEY = os.environ.get("STRIPE_LIVE_SECRET_KEY", "xxxx")
STRIPE_TEST_PUBLIC_KEY = STRIPE_PUBLIC_KEY
STRIPE_TEST_SECRET_KEY = STRIPE_SECRET_KEY
STRIPE_LIVE_MODE = False  # Change to True in production

ALERTS_YEAR_PLAN = "follow100"
SUBSCRIPTION_MONTH_ONE_PLAN = "subscription_month_one"
SUBSCRIPTION_MONTH_FULL_PLAN = "subscription_month_full"
SUBSCRIPTION_YEAR_PLAN = "subscription_year"
API_MONTH_PLAN = "api_month"
API_YEAR_PLAN = "api_year"

PARSER = 'borme.parser.backend.bormeparser'
#PARSER = 'borme.parser.backend.yabormeparser'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 7
REGISTRATION_OPEN = True

STATIC_ROOT = os.path.join(SITE_ROOT, 'static')
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

# django-maintenance-mode
MAINTENANCE_MODE = False  # Set to True to enable maintenance mode
MAINTENANCE_MODE_IGNORE_STAFF = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True

# user
AUTH_USER_MODEL = 'alertas.User'
