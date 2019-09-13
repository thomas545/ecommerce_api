from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status
from .serializers import (OrderItemSerializer, OrderItemMiniSerializer, 
                            OrderSerializer, OrderMiniSerializer)
from .models import Order, OrderItem
from user_profile.models import Address
from .models import Product
from django.contrib.auth.models import User

class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        user_address = Address.objects.filter(user=user, primary=True).first()
        product = get_object_or_404(Product, pk=pk)
        try:
            order_number = request.data.get("order_number", '')
        except :
            pass
        total = product.quantity * product.price
        order = Order.objects.create(buyer=user, order_number=order_number, 
                                        address=user_address, is_paid=True)
        OrderItem().create_order_item(order, product, product.quantity, total)
        # TODO Payment Integration here.
        # TODO push notifications and Email
        return Response("Your order created successfully.")

        
