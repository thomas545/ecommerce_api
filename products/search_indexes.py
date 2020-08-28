from haystack import indexes
from .models import Product


class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    title = indexes.CharField(model_attr="title")
    category = indexes.CharField()

    def get_model(self):
        return Product

    def prepare_category(self, obj):
        return obj.category.name

    def index_queryset(self, using=None):
        return self.get_model().objects.all().select_related("category", "seller")
