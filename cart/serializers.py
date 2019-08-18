from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['quantity', 'price']




class CartItemSerializer(serializers.ModelSerializer):
    # product = CartProductSerializer(required=False)
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity']

