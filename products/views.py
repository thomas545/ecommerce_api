from django.core.cache import cache
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from django_elasticsearch_dsl_drf.constants import LOOKUP_FILTER_GEO_DISTANCE
from django_elasticsearch_dsl_drf.filter_backends import (FilteringFilterBackend, OrderingFilterBackend, 
                                                SearchFilterBackend, DefaultOrderingFilterBackend)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet


from .models import Category, Product, ProductViews
from .serializers import (CategoryListSerializer, ProductSerializer,
                        CreateProductSerializer, ProductViewsSerializer, 
                        ProductDetailSerializer, ProductMiniSerializer, ProductDocumentSerializer)
from .document import ProductDocument
from .permissions import IsOwnerAuth
from notifications.utils import push_notifications
from notifications.twilio import send_message


class CategoryListAPIView(ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategoryListSerializer
    filter_backends = (DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter,)
    search_fields = ('name',)
    ordering_fields = ('created',)
    filter_fields = ('created',)
    # queryset = Category.objects.all()

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset

class CategoryAPIView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategoryListSerializer
    queryset = Category.objects.all()


class ListProductAPIView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter,)
    search_fields = ('title',)
    ordering_fields = ('created',)
    filter_fields = ('views',)
    queryset = Product.objects.all()

    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     # we did cache but not use it yet.
    #     # if 'result' in cache:
    #     #     serializer = self.get_serializer(queryset, many=True)
    #     #     serializer = cache.get('result')
    #     # else:
    #     #     serializer = self.get_serializer(queryset, many=True)
    #     #     cache.set('result', serializer.data, timeout=DEFAULT_TIMEOUT)
    #     return queryset

    # Cache requested url for each user for 2 hours
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ListUserProductAPIView(ListAPIView):
    serializer_class = ProductSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter,)
    search_fields = ('title','user__username',)
    ordering_fields = ('created',)
    filter_fields = ('views',)

    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.filter(user=user)
        return queryset

class CreateProductAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateProductSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        push_notifications(request.user, request.data['title'], "you have add a new product")
        if user.profile.phone_number:
            send_message(user.profile.phone_number, "Congratulations, you Created New Product")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class DestroyProductAPIView(DestroyAPIView):
    permission_classes = [IsOwnerAuth]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()

class ProductViewsAPIView(ListAPIView):
    # permission_classes = [IsOwnerAuth]
    serializer_class = ProductViewsSerializer
    queryset = ProductViews.objects.all()


class ProductDetailView(APIView):

    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if not ProductViews.objects.filter(product=product, ip=ip).exists():
            ProductViews.objects.create(product=product, ip=ip)

            product.views += 1
            product.save()
        serializer = ProductDetailSerializer(product, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = request.user
        product = get_object_or_404(Product, pk=pk)
        if product.user != user:
            raise PermissionDenied("this product don't belong to you.")

        serializer = ProductDetailSerializer(product, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

