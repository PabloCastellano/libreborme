from django_elasticsearch_dsl import DocType, fields, Index
from .models import Company, Person

idx = Index('libreborme')
idx.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@idx.doc_type
class CompanyDocument(DocType):
    name = fields.TextField(attr="fullname")

    class Meta:
        model = Company

        fields = [
            'slug',
        ]


@idx.doc_type
class PersonDocument(DocType):
    class Meta:
        model = Person

        fields = [
            'name',
            'slug',
        ]


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
        if self._count is None:
            result = self.client.search(*self.args, **self.kwargs)['hits']
        return result['total']

    def __len__(self):
        return self.count()

    def __getitem__(self, key):
        if not isinstance(key, slice):
            raise ElasticSearchPaginatorListException('key parameter in __getitem__ is not a slice instance')
        self.kwargs['from_'] = key.start
        self.kwargs['size'] = key.stop - key.start
        return self.client.search(*self.args, **self.kwargs)['hits']['hits']
