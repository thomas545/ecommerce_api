from django.db import models
from core.models import TimeStampedModel, Extensions
from django.contrib.auth import get_user_model
from user_profile.models import Address
from products.models import Product


UserModel = get_user_model()


class Order(Extensions):
    PENDING_STATE = "p"
    COMPLETED_STATE = "c"

    ORDER_CHOICES = ((PENDING_STATE, "pending"), (COMPLETED_STATE, "completed"))

    buyer = models.ForeignKey(UserModel, related_name="order", on_delete=models.CASCADE)
    order_number = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(
        max_length=1, choices=ORDER_CHOICES, default=PENDING_STATE
    )
    is_paid = models.BooleanField(default=False)
    address = models.ForeignKey(
        Address, related_name="order_address", on_delete=models.CASCADE
    )

    @staticmethod
    def create_order(buyer, order_number, address, is_paid=False):
        order = Order()
        order.buyer = buyer
        order.order_number = order_number
        order.address = address
        order.is_paid = is_paid
        order.save()
        return order


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(
        Order, related_name="order_items", on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product, related_name="product_order", on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    @staticmethod
    def create_order_item(order, product, quantity, total):
        order_item = OrderItem()
        order_item.order = order
        order_item.product = product
        order_item.quantity = quantity
        order_item.total = total
        order_item.save()
        return order_item
