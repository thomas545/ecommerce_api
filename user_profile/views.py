from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialConnectView
from rest_auth.social_serializers import TwitterConnectSerializer

from .models import Profile, Address
from .serializers import ProfileSerializer, UserSerializer, AddressSerializer, CreateAddressSerializer
from django.contrib.auth.models import User


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'username'

class ListAddressAPIView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Address.objects.filter(user=user)
        return queryset

class AddressDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer
    queryset = Address.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        address = self.get_object()
        if address.user != user:
            raise NotAcceptable("this addrss don't belong to you")
        serializer = self.get_serializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)

class createAddressAPIView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CreateAddressSerializer
    queryset = ''

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, primary=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FacebookConnectView(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter

class TwitterConnectView(SocialConnectView):
    serializer_class = TwitterConnectSerializer
    adapter_class = TwitterOAuthAdapter