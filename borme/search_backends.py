from haystack.backends.elasticsearch_backend import ElasticsearchSearchBackend
from haystack.backends.elasticsearch_backend import ElasticsearchSearchEngine


class AsciifoldingElasticBackend(ElasticsearchSearchBackend):

    def __init__(self, *args, **kwargs):
        super(AsciifoldingElasticBackend, self).__init__(*args, **kwargs)
        analyzer = {
            "ascii_analyser": {
                "tokenizer": "standard",
                "filter": ["standard", "asciifolding", "lowercase"]
            },
            "ngram_analyzer": {
                "type": "custom",
                "tokenizer": "lowercase",
                "filter": ["haystack_ngram", "asciifolding"]
            },
            "edgengram_analyzer": {
                "type": "custom",
                "tokenizer": "lowercase",
                "filter": ["haystack_edgengram", "asciifolding"]
            }
        }
        self.DEFAULT_SETTINGS['settings']['analysis']['analyzer'] = analyzer

    def build_schema(self, fields):
        content_field_name, mapping = super(AsciifoldingElasticBackend, self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and not field_class.field_type in('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = "ascii_analyser"

            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class AsciifoldingElasticSearchEngine(ElasticsearchSearchEngine):
    backend = AsciifoldingElasticBackend
