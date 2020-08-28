""" Here write a code of viewsets """
from rest_framework import viewsets
from drf_haystack.viewsets import HaystackViewSet
from .models import Product
from .serializers import ProductIndexSerializer



class ProductSearchView(HaystackViewSet):

    # `index_models` is an optional list of which models you would like to include
    # in the search result. You might have several models indexed, and this provides
    # a way to filter out those of no interest for this particular view.
    # (Translates to `SearchQuerySet().models(*index_models)` behind the scenes.
    index_models = [Product]
    serializer_class = ProductIndexSerializer
    queryset = Product.objects.all()
