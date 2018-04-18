from django.contrib.postgres.search import SearchQuery
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


# q_companies = Company.objects.filter(name__icontains=self.request.GET['q'])
# q_companies = Company.objects.annotate(rank=SearchRank(F('document'), query)).filter(rank__gt=0.01).order_by('-rank')
def search_fts(raw_query, model):
    words = raw_query.split()
    query = SearchQuery(words[0])
    for word in words[1:]:
        # AND
        query &= SearchQuery(word)
    return model.objects.filter(document=query)
