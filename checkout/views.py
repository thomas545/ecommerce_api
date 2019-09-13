from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, DestroyAPIView
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView


class CheckoutView(APIView):
    pass


class CheckoutCartView(APIView):
    pass
