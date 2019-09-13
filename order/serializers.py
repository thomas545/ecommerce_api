from rest_framework import serializers
from .models import Order, OrderItem
from user_profile.serializers import AddressSerializer
from products.serializers import ProductDetailSerializer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"


class OrderMiniSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False, read_only=True)
    class Meta:
        model = Order
        fields = "__all__"

 
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"

class OrderItemMiniSerializer(serializers.ModelSerializer):
    order = OrderMiniSerializer(required=False, read_only=True)
    product = ProductDetailSerializer(required=False, read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"