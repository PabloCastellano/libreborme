from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

import os


def _check_permissions():
    # Borme files directories
    if not os.path.isdir(settings.BORME_ROOT):
        raise ImproperlyConfigured("The directory does not exist: " + settings.BORME_ROOT)
    if not os.path.isdir(settings.BORME_PDF_ROOT):
        raise ImproperlyConfigured("The directory does not exist: " + settings.BORME_PDF_ROOT)
    if not os.path.isdir(settings.BORME_XML_ROOT):
        raise ImproperlyConfigured("The directory does not exist: " + settings.BORME_XML_ROOT)
    if not os.path.isdir(settings.BORME_JSON_ROOT):
        raise ImproperlyConfigured("The directory does not exist: " + settings.BORME_JSON_ROOT)
    if not os.path.isdir(settings.BORME_SUBSCRIPTIONS_ROOT):
        raise ImproperlyConfigured("The directory does not exist: " + settings.BORME_SUBSCRIPTIONS_ROOT)

    # These are only defined in staging and produciton environments
    # If they are defined, they have to exist
    try:
        if not os.access(settings.BORME_LOG_ROOT, os.W_OK):
            raise ImproperlyConfigured("The logs directory is not writable: " + settings.BORME_LOG_ROOT)
    except AttributeError:
        pass

    try:
        log_file = settings.LOGGING['handlers']['applogfile']['filename']
        if not os.access(log_file, os.W_OK):
            raise ImproperlyConfigured("The log file is not writable: " + log_file)
    except KeyError:
        pass


def check_permissions():

    try:
        _check_permissions()
    except ImproperlyConfigured as e:
        if settings.DEBUG == False:
            raise
        print("\n\n")
        print("!!!!!!!!!!!!!!! Sanity check failed !!!!!!!!!!!!!!")
        print(e)
        print("\n\n")
