from django_elasticsearch_dsl import Document, Index #, fields
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl.registries import registry
from .models import Product




# Name of the Elasticsearch index
product = Index('product')

# See Elasticsearch Indices API reference for available settings
product.settings(
    number_of_shards=1,
    number_of_replicas=1
)

@registry.register_document
class ProductDocument(Document):

    class Django:
        model = Product
        fields = ['id', 'title', 'quantity']

    # class Meta:
    #     model = Product
    #     fields = ('id', 'title',)