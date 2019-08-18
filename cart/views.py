from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from .serializers import CartItemSerializer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, ValidationError, PermissionDenied

from .models import Cart, CartItem
from products.models import Product


class CartItemAPIView(ListCreateAPIView):
    serializer_class = CartItemSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.filter(cart__user=11)
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=11)
        product = get_object_or_404(Product, pk=request.data['product'])
        current_item = CartItem.objects.filter(cart=cart, product=product)
        
        if user == product.user:
            raise PermissionDenied("This Is Your Product")

        if current_item.count() > 0:
            raise NotAcceptable("You already have this item in your shopping cart")

        try:
            quantity = int(request.data['quantity'])
        except Exception as e:
            raise ValidationError("Please Enter Your Quantity")
        
        if quantity > product.quantity:
            raise NotAcceptable("You order quantity more than the seller have")

        cart_item = CartItem(cart=cart, product=product, quantity=quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        total = float(product.price) * float(quantity)
        cart.total = total
        cart.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    