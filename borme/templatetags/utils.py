# -*- coding: utf-8 -*-

from django.template.defaulttags import register
from django.utils.text import slugify

from bormeparser.regex import is_acto_cargo as es_acto_cargo

import datetime

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
def is_acto_cargo2(val):
    return es_acto_cargo(val)


@register.filter
def is_string(val):
    return isinstance(val, str)


@register.filter
def is_bool(val):
    return isinstance(val, bool)


@register.filter(name='get_class')
def get_class(val):
  return val.__class__.__name__


# https://djangosnippets.org/snippets/401/
@register.filter
def rows_distributed(thelist, n):
    """
    Break a list into ``n`` rows, distributing columns as evenly as possible
    across the rows. For example::

        >>> l = range(10)

        >>> rows_distributed(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> rows_distributed(l, 3)
        [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]

        >>> rows_distributed(l, 4)
        [[0, 1, 2], [3, 4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

        >>> rows_distributed(l, 9)
        [[0, 1], [2], [3], [4], [5], [6], [7], [8], [9]]

        # This filter will always return `n` rows, even if some are empty:
        >>> rows(range(2), 3)
        [[0], [1], []]
    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    list_len = len(thelist)
    split = list_len // n

    remainder = list_len % n
    offset = 0
    rows = []
    for i in range(n):
        if remainder:
            start, end = (split+1)*i, (split+1)*(i+1)
        else:
            start, end = split*i+offset, split*(i+1)+offset
        rows.append(thelist[start:end])
        if remainder:
            remainder -= 1
            offset += 1
    return rows


@register.filter
def date_isoformat(date):
    if isinstance(date, datetime.datetime):
        date = date.date()
    return date.isoformat()


@register.filter
def slug(val):
  return slugify(val)
