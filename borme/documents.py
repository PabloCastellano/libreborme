from django_elasticsearch_dsl import DocType, Index
from .models import Company, Person

idx = Index("libreborme")
idx.settings(
    number_of_shards=1,
    number_of_replicas=0
)


@idx.doc_type
class CompanyDocument(DocType):
    class Meta:
        model = Company

        fields = ["name"]
        queryset_pagination = 25
        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True
        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False


@idx.doc_type
class PersonDocument(DocType):
    class Meta:
        model = Person

        fields = ["name"]
        queryset_pagination = 25
        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True
        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False
