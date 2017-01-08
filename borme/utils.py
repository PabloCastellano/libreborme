from bormeparser.regex import regex_empresa_tipo

from django.db import connection
from django.utils.text import slugify

# http://chase-seibert.github.io/blog/2012/06/01/djangopostgres-optimize-count-by-replacing-with-an-estimate.html
# TODO: exception if db engine is not postgres as in https://github.com/stephenmcd/django-postgres-fuzzycount/blob/master/fuzzycount.py
def estimate_count_fast(table):
    ''' postgres really sucks at full table counts, this is a faster version
    see: http://wiki.postgresql.org/wiki/Slow_Counting '''
    cursor = connection.cursor()
    cursor.execute("select reltuples from pg_class where relname='%s';" % table)
    row = cursor.fetchone()
    return int(row[0])


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