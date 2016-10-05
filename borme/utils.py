from django.db import connection


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


def get_file(name):
    """ Si existe el archivo, prueba con name.1, name.2, ...
        hasta que no exista y devuelve su descriptor """
    counter = 0
    base_name = name
    while os.path.exists(name):
        counter += 1
        name = base_name + "." + str(counter)
    return open(name, "w+")
