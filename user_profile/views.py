from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets
from rest_framework.views import APIView
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
    GenericAPIView,
    RetrieveUpdateAPIView,
    UpdateAPIView,
)
from rest_framework.exceptions import PermissionDenied, NotAcceptable, ValidationError

from allauth.account.views import ConfirmEmailView
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialConnectView, SocialLoginView
from rest_auth.social_serializers import TwitterConnectSerializer
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from rest_auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
    LogoutView,
)
from rest_auth.serializers import PasswordResetConfirmSerializer
from rest_auth.registration.views import RegisterView, VerifyEmailView
from rest_auth.registration.serializers import VerifyEmailSerializer
from rest_auth.app_settings import JWTSerializer
from rest_auth.utils import jwt_encode
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User, Permission
from django.utils.translation import ugettext_lazy as _
from .models import Profile, Address, SMSVerification, DeactivateUser, NationalIDImage
from .serializers import (
    ProfileSerializer,
    UserSerializer,
    AddressSerializer,
    CreateAddressSerializer,
    SMSVerificationSerializer,
    SMSPinSerializer,
    DeactivateUserSerializer,
    PermissionSerializer,
    PasswordChangeSerializer,
    UserPermissionSerializer,
    NationalIDImageSerializer,
)
from .send_mail import send_register_mail, send_reset_password_email

sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters("password1", "password2")
)


class DeactivateUserView(CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DeactivateUserSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        # TODO validation and try exception
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response("your account will deactivate after 30 days.")


class CanselDeactivateUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # TODO validation and try exception
        deactivate = DeactivateUser.objects.get(user=user)
        deactivate.deactive = False
        deactivate.save()
        user.is_active = True
        user.save()
        return Response("your account will activated.")


class LoginAPIView(LoginView):
    queryset = ""

    def get_response(self):
        serializer_class = self.get_response_serializer()
        if getattr(settings, "REST_USE_JWT", False):
            data = {"user": self.user, "token": self.token}
            serializer = serializer_class(
                instance=data, context={"request": self.request}
            )
        else:
            serializer = serializer_class(
                instance=self.token, context={"request": self.request}
            )
        response = Response(serializer.data, status=status.HTTP_200_OK)

        deactivate = DeactivateUser.objects.filter(user=self.user, deactive=True)
        if deactivate:
            deactivate.update(deactive=False)
        return response

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(
            data=self.request.data, context={"request": request}
        )
        self.serializer.is_valid(raise_exception=True)
        self.login()
        return self.get_response()


class RegisterAPIView(RegisterView):
    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(RegisterAPIView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        if getattr(settings, "REST_USE_JWT", False):
            data = {"user": user, "token": self.token}
        return JWTSerializer(data).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(
            self.get_response_data(user),
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if getattr(settings, "REST_USE_JWT", False):
            self.token = jwt_encode(user)

        email = EmailAddress.objects.get(email=user.email, user=user)
        confirmation = EmailConfirmationHMAC(email)
        key = confirmation.key
        # TODO Send mail confirmation here .
        # send_register_mail.delay(user, key)
        print("account-confirm-email/" + key)
        return user


class ResendSMSAPIView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = SMSVerificationSerializer
    allowed_methods = ("POST",)

    def resend_or_create(self):
        phone = self.request.data.get("phone")
        send_new = self.request.data.get("new")
        sms_verification = None

        user = User.objects.filter(profile__phone_number=phone).first()

        if not send_new:
            sms_verification = (
                SMSVerification.objects.filter(user=user, verified=False)
                .order_by("-created")
                .first()
            )

        if sms_verification is None:
            sms_verification = SMSVerification.objects.create(user=user, phone=phone)

        return sms_verification.send_confirmation()

    def post(self, request, *args, **kwargs):
        success = self.resend_or_create()

        return Response(dict(success=success), status=status.HTTP_200_OK)


class VerifySMSView(APIView):
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD")

    def get_serializer(self, *args, **kwargs):
        return SMSPinSerializer(*args, **kwargs)

    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pin = int(request.data.get("pin"))
        # TODO get user SMSVerification instead of below confirmation variable
        confirmation = get_object_or_404(SMSVerification, pk=pk)
        confirmation.confirm(pin=pin)
        return Response("Your Phone Number Is Verfied.", status=status.HTTP_200_OK)


class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        profile = Profile.objects.get(pk=pk)
        serializer = ProfileSerializer(profile, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"


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
    queryset = ""

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, primary=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FacebookConnectView(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class TwitterConnectView(SocialLoginView):
    serializer_class = TwitterConnectSerializer
    adapter_class = TwitterOAuthAdapter


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    callback_url = "https://www.google.com"


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):

        email = request.data.get("email", None)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise NotAcceptable(_("Please enter a valid email."))
        send_reset_password_email.delay(user)
        return Response(
            {"detail": _("Password reset e-mail has been sent.")},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordResetConfirmSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordResetConfirmView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Password has been reset with the new password.")})


class PasswordChangeView(GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PasswordChangeSerializer

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(PasswordChangeView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("Congratulations, password has been Changed.")})


class VerifyEmailView(APIView, ConfirmEmailView):
    permission_classes = (permissions.AllowAny,)
    allowed_methods = ("POST", "OPTIONS", "HEAD")

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs["key"] = serializer.validated_data["key"]
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({"detail": _("ok")}, status=status.HTTP_200_OK)


class RetrievePermissionView(RetrieveAPIView):
    serializer_class = UserPermissionSerializer
    queryset = User.objects.all()
    lookup_field = "username"


class UpdatePermissionView(UpdateAPIView):
    serializer_class = UserPermissionSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     partial = True
    #     return super(UpdatePermissionView, self).update(request, *args, **kwargs)


class NationalIDImageViewSet(viewsets.ModelViewSet):
    serializer_class = NationalIDImageSerializer
    queryset = NationalIDImage.objects.all().select_related("user")