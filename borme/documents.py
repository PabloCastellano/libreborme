from django_elasticsearch_dsl import DocType, Index
from .models import Company, Person

idx = Index('libreborme')
idx.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@idx.doc_type
class CompanyDocument(DocType):
    class Meta:
        model = Company

        fields = [
            'name',
            'slug',
        ]

        # Paginate the django queryset used to populate the index with the specified size
        # (by default there is no pagination)
        # queryset_pagination = 5000


@idx.doc_type
class PersonDocument(DocType):
    class Meta:
        model = Person

        fields = [
            'name',
            'slug',
        ]

        # Paginate the django queryset used to populate the index with the specified size
        # (by default there is no pagination)
        # queryset_pagination = 5000
