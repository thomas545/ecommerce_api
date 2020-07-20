from django_elasticsearch_dsl import Document, Index, fields
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl.registries import registry
from .models import Product


products_index = Index("products")
products_index.settings(number_of_shards=1, number_of_replicas=1)

html_strip = analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["standard", "lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


# @registry.register_document
@products_index.doc_type
class ProductDocument(Document):

    # id = fields.IntegerField(attr='id')
    # title = fields.StringField(
    #     analyzer=html_strip,
    #     fields={
    #         'raw': fields.StringField(analyzer='keyword'),
    #     }
    # )
    # description = fields.TextField(
    #     analyzer=html_strip,
    #     fields={
    #         'raw': fields.TextField(analyzer='keyword'),
    #     }
    # )
    # quantity = fields.IntegerField(attr='quantity')
    # created = fields.DateField()

    class Django(object):
        model = Product

    # class Django:
    #     model = Product
    #     fields = ['id', 'title', 'quantity']
