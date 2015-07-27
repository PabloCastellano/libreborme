# -*- coding: utf-8 -*-

from django.template.defaulttags import register
from borme.models import CargoPerson, CargoCompany

#from borme_parser import DICT_KEYWORDS
DICT_KEYWORDS = {}  # FIXME

DICT_NAMES = {v: k for k, v in DICT_KEYWORDS.items()}
DICT_NAMES['id_acto'] = 'ID acto'


# http://stackoverflow.com/a/8000091
@register.filter
def get_item(object, attribute):
    return object.__getattribute__(attribute)
    #return dictionary.get(key)


@register.filter
def get_url(object, attribute):
    return object.get(attribute).url


@register.filter
def nombre(object):
    try:
        return DICT_NAMES[object]
    except:
        return object


@register.filter
def is_acto_cargo(val):
    return isinstance(val, CargoPerson) or isinstance(val, CargoCompany)


@register.filter
def is_string(val):
    return isinstance(val, str)
