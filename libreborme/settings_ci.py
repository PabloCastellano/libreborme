import os

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

# BORME
BORME_ROOT = CONFIG['borme_root']
BORME_PDF_ROOT = os.path.join(BORME_ROOT, 'pdf')
BORME_XML_ROOT = os.path.join(BORME_ROOT, 'xml')
BORME_JSON_ROOT = os.path.join(BORME_ROOT, 'json')

# PARSER = 'borme.parser.backend.yabormeparser'
