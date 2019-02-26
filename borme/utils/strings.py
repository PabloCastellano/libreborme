from django.utils.text import slugify

from bormeparser.regex import regex_empresa_tipo

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
logger.addHandler(ch)
logger.setLevel(logging.INFO)


def convertir_iniciales(name):
    iniciales = []
    iniciales.append(name[0])
    esp_index = name.find(' ')
    while esp_index != -1:
        iniciales.append(name[esp_index + 1])
        esp_index = name.find(' ', esp_index + 1)
    return '. '.join(iniciales) + '.'


def empresa_slug(nombre):
    """ Dado el nombre completo de la sociedad, incluyendo el tipo (SL, SA, ...),
        devuelve el slug de la sociedad.
    """
    empresa, _ = regex_empresa_tipo(nombre)
    return slugify(empresa)


def parse_empresa(nombre):
    empresa, tipo = regex_empresa_tipo(nombre)
    slug_c = slugify(empresa)

    return empresa, tipo, slug_c
