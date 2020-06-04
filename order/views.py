from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework import permissions, status, exceptions
from .serializers import (
    OrderItemSerializer,
    OrderItemMiniSerializer,
    OrderSerializer,
    OrderMiniSerializer,
)
from .models import Order, OrderItem
from user_profile.models import Address
from .models import Product
from notifications.utils import push_notifications
from core.decorators import time_calculator


class OrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @time_calculator
    def time(self):
        return 0

    def post(self, request, pk, *args, **kwargs):
        user = request.user
        user_address = Address.objects.filter(user=user, primary=True).first()
        product = get_object_or_404(Product, pk=pk)
        if product.quantity == 0:
            raise exceptions.NotAcceptable("quantity of this product is out.")
        try:
            order_number = request.data.get("order_number", "")
            quantity = request.data.get("quantity", 1)
        except:
            pass

        total = quantity * product.price
        order = Order().create_order(user, order_number, user_address, True)
        order_item = OrderItem().create_order_item(order, product, quantity, total)
        serializer = OrderItemMiniSerializer(order_item)
        push_notifications(
            user,
            "Request Order",
            "your order: #" + str(order_number) + " has been sent successfully.",
        )
        self.time()
        # TODO Payment Integration here.
        # TODO send Email to seller and buyer
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def Payment(request):
    return render(request, "payment/payment.html", {})
