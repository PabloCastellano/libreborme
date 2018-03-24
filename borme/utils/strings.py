from django.utils.text import slugify

from bormeparser.regex import regex_empresa_tipo


def convertir_iniciales(name):
    iniciales = []
    iniciales.append(name[0])
    esp_index = name.find(' ')
    while esp_index != -1:
        iniciales.append(name[esp_index + 1])
        esp_index = name.find(' ', esp_index + 1)
    return '. '.join(iniciales) + '.'


def slug2(val):
    """ Dado el nombre completo de la sociedad, incluyendo el tipo (SL, SA, ...),
        devuelve el slug de la sociedad.
    """
    empresa, _ = regex_empresa_tipo(val)
    return slugify(empresa)
