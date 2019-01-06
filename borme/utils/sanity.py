from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import os


def check_permissions():
    if not os.path.isdir(settings.BORME_ROOT):
        raise ImproperlyConfigured("The directory doesn not exist: " + settings.BORME_ROOT)
    if not os.path.isdir(settings.BORME_PDF_ROOT):
        raise ImproperlyConfigured("The directory doesn not exist: " + settings.BORME_PDF_ROOT)
    if not os.path.isdir(settings.BORME_XML_ROOT):
        raise ImproperlyConfigured("The directory doesn not exist: " + settings.BORME_XML_ROOT)
    if not os.path.isdir(settings.BORME_JSON_ROOT):
        raise ImproperlyConfigured("The directory doesn not exist: " + settings.BORME_JSON_ROOT)
    try:
        log_file = settings.LOGGING['handlers']['applogfile']['filename']
        if not os.access(log_file, os.W_OK):
            raise ImproperlyConfigured("The file is not writable: " + log_file)
    except KeyError:
        pass
