from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListCreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from .serializers import CartItemSerializer, CartItemUpdateSerializer
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotAcceptable, ValidationError, PermissionDenied
from django.utils.translation import ugettext_lazy as _

from .models import Cart, CartItem
from products.models import Product
from notifications.utils import push_notifications


class CartItemAPIView(ListCreateAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CartItem.objects.filter(cart__user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        user = request.user
        cart = get_object_or_404(Cart, user=user)
        product = get_object_or_404(Product, pk=request.data["product"])
        current_item = CartItem.objects.filter(cart=cart, product=product)

        if user == product.user:
            raise PermissionDenied("This Is Your Product")

        if current_item.count() > 0:
            raise NotAcceptable("You already have this item in your shopping cart")

        try:
            quantity = int(request.data["quantity"])
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
        push_notifications(
            cart.user,
            "New cart product",
            "you added a product to your cart " + product.title,
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemView(RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    # method_serializer_classes = {
    #     ('PUT',): CartItemUpdateSerializer
    # }
    queryset = CartItem.objects.all()

    def retrieve(self, request, *args, **kwargs):
        cart_item = self.get_object()
        if cart_item.cart.user != request.user:
            raise PermissionDenied("Sorry this cart not belong to you")
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        print(request.data)
        product = get_object_or_404(Product, pk=request.data["product"])

        if cart_item.cart.user != request.user:
            raise PermissionDenied("Sorry this cart not belong to you")

        try:
            quantity = int(request.data["quantity"])
        except Exception as e:
            raise ValidationError("Please, input vaild quantity")

        if quantity > product.quantity:
            raise NotAcceptable("Your order quantity more than the seller have")

        serializer = CartItemUpdateSerializer(cart_item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        if cart_item.cart.user != request.user:
            raise PermissionDenied("Sorry this cart not belong to you")
        cart_item.delete()
        push_notifications(
            cart_item.cart.user,
            "deleted cart product",
            "you have been deleted this product: "
            + cart_item.product.title
            + " from your cart",
        )

        return Response(
            {"detail": _("your item has been deleted.")},
            status=status.HTTP_204_NO_CONTENT,
        )
