from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Category, Product, ProductViews
from .serializers import (CategoryListSerializer, ProductSerializer,
                        CreateProductSerializer, ProductViewsSerializer,ProductDetailSerializer)

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
    search_fields = ('title','user__username',)
    ordering_fields = ('created',)
    filter_fields = ('views',)
    queryset = Product.objects.all()

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = Product.objects.filter(user=user)
    #     return queryset

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
    

