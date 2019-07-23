from django.conf import settings
from django.core.paginator import Paginator
from django_elasticsearch_dsl import DocType, fields, Index
from elasticsearch_dsl import analyzer, token_filter
from .models import Company, Person

import elasticsearch


ELASTICSEARCH_INDEX = settings.DATABASES['default']['NAME']


def configure_index(idx):
    """Configure ES index settings.

    NOTE: This is unused at the moment. Current issues:
    1. The index needs to be created (index.create() or search_index --create)
    setting update_all_types=True because of the attribute name being the same
    in Person and Company.
    https://elasticsearch-py.readthedocs.io/en/master/api.html#elasticsearch.client.IndicesClient.create

    name = fields.TextField(attr="fullname", analyzer=lb_analyzer)

    2. How to specifiy token filter for an attribute?

    Therefore the index needs to be configured outside Django.
    """
    idx.settings(number_of_shards=1, number_of_replicas=0)
    lb_filter = token_filter(
        "lb_filter",
        "stop",
        stopwords=["i"]
    )
    lb_analyzer = analyzer(
        "lb_analyzer",
        tokenizer="standard",
        filter=["standard", "lb_filter", "asciifolding", "lowercase"]
    )
    return lb_analyzer, lb_filter


idx = Index(ELASTICSEARCH_INDEX)
# lb_analyzer, lb_filter = configure_index(idx)


# TODO: NIF
@idx.doc_type
class CompanyDocument(DocType):
    name = fields.TextField(attr="fullname")

    class Meta:
        model = Company
        fields = ['slug']
        doc_type = "company"


@idx.doc_type
class PersonDocument(DocType):
    class Meta:
        model = Person
        fields = ['name', 'slug']
        doc_type = "person"


class ElasticSearchPaginatorListException(Exception):
    pass


# Originally from http://epoz.org/blog/django-paginator-elasticsearch.html
# Modified count() method to work with elasticsearch 5.x
class ElasticSearchPaginatorList(object):
    def __init__(self, client, *args, **kwargs):
        self.client = client
        self.args = args
        self.kwargs = kwargs
        self._count = None

    def count(self):
        """Warning: result is cached using initial kwargs"""
        if self._count is None:
            # self.client.search(*self.args, **self.kwargs)['hits']['total']
            result = self.client.count(index=self.kwargs['index'],
                                       doc_type=self.kwargs['doc_type'],
                                       body=self.kwargs['body'])
            self._count = result['count']
        return self._count

    def __len__(self):
        return self.count()

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise ElasticSearchPaginatorListException(
                    'key parameter in __getitem__ is not a slice instance')
        self.kwargs['from_'] = key.start
        self.kwargs['size'] = key.stop - key.start
        return self.client.search(*self.args, **self.kwargs)['hits']['hits']


def es_search_paginator(doc_type, text):
    """Perform an ElasticSearch query and return a paginable object.

    For full details of accepted parameters in ES query:
    https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl-match-query.html
    https://www.elastic.co/guide/en/elasticsearch/reference/5.6/query-dsl-query-string-query.html

    :param doc_type: ES document name ('person' or 'company')
    :param query: Text to search
    :type doc_type: str
    :type query: str
    :rtype: (ElasticSearchPaginatorList)
    """

    # It is a better idea to use match query type because it doesn't go through
    # a "query parsing" process". It does not support field name prefixes,
    # wildcard characters, or other "advanced" features, but chances of
    # failing are non existent.
    # A parsed query will fail if it contains a colon or a curly brace
    """
    es_query = {
        "query": {
            "query_string": {
                "default_field": "name",
                "default_operator": "AND",
                "query": text,
                "allow_leading_wildcard": "false",
                "fuzziness": 0
            }
        }
    }
    """

    es_query = {
        "query": {
            "match": {
                "name": {
                    "query": text,
                    "operator": "AND"
                }
            }
        }
    }
    es = elasticsearch.Elasticsearch(settings.ELASTICSEARCH_URI)
    results = ElasticSearchPaginatorList(
            es, body=es_query,
            index=ELASTICSEARCH_INDEX, doc_type=doc_type)

    return results
