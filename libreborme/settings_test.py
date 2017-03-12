from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'libreborme',
        'USER': 'libreborme',
        'PASSWORD': 'password',
        'HOST': 'localhost',
#        'PORT': '',
    }
}
