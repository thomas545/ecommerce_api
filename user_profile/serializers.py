from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.forms import SetPasswordForm
from rest_framework import serializers, exceptions
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from allauth.account.models import EmailAddress
from .models import Profile, Address, SMSVerification, DeactivateUser, NationalIDImage

# Get the UserModel
UserModel = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(style={"input_type": "password"})

    def authenticate(self, **kwargs):
        return authenticate(self.context["request"], **kwargs)

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include "username or "email" or "phone number" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = self.authenticate(email=email, password=password)
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            msg = _(
                'Must include either "username" or "email" or "phone number" and "password".'
            )
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = None

        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.EMAIL
            ):
                user = self._validate_email(email, password)

            # Authentication through username
            elif (
                app_settings.AUTHENTICATION_METHOD
                == app_settings.AuthenticationMethod.USERNAME
            ):
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            if username:
                user = self._validate_username_email(username, "", password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _("User account is inactive.")
                raise exceptions.ValidationError(msg)
        else:
            msg = _("please check your username or email or phone number or password.")
            raise exceptions.ValidationError(msg)

        # TODO user can't login if phone number and email address not verified.

        # If required, is the email verified?
        if "rest_auth.registration" in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            if (
                app_settings.EMAIL_VERIFICATION
                == app_settings.EmailVerificationMethod.MANDATORY
            ):
                try:
                    email_address = user.emailaddress_set.get(email=user.email)
                except EmailAddress.DoesNotExist:
                    raise serializers.ValidationError(
                        _(
                            "This account don't have E-mail address!, so that you can't login."
                        )
                    )
                if not email_address.verified:
                    raise serializers.ValidationError(_("E-mail is not verified."))

        # If required, is the phone number verified?
        try:
            phone_number = user.sms  # .get(phone=user.profile.phone_number)
        except SMSVerification.DoesNotExist:
            raise serializers.ValidationError(
                _("This account don't have Phone Number!")
            )
        if not phone_number.verified:
            raise serializers.ValidationError(_("Phone Number is not verified."))

        attrs["user"] = user
        return attrs


class DeactivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeactivateUser
        exclude = ["deactive", "user"]


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    birth_date = serializers.CharField(required=True, write_only=True)
    phone_number = PhoneNumberField(
        required=True,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=Profile.objects.all(),
                message=_("A user is already registered with this phone number."),
            )
        ],
    )

    def get_cleaned_data_profile(self):
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            "birth_date": self.validated_data.get("birth_date", ""),
            "phone_number": self.validated_data.get("phone_number", ""),
        }

    def create_profile(self, user, validated_data):
        user.first_name = self.validated_data.get("first_name")
        user.last_name = self.validated_data.get("last_name")
        user.save()

        user.profile.birth_date = self.validated_data.get("birth_date")
        user.profile.phone_number = self.validated_data.get("phone_number")
        user.profile.save()

    def custom_signup(self, request, user):
        self.create_profile(user, self.get_cleaned_data_profile())


class SMSVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSVerification
        exclude = "modified"


class SMSPinSerializer(serializers.Serializer):
    pin = serializers.IntegerField()


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    gender = serializers.SerializerMethodField()
    profile_picture = Base64ImageField()

    def get_gender(self, obj):
        return obj.get_gender_display()

    class Meta:
        model = Profile
        fields = ["user", "profile_picture", "phone_number", "gender", "about"]

    """
    TODO update profile and if phone Number not verified user can't update in his profile.
    """


class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.profile_picture")
    gender = serializers.CharField(source="profile.gender")
    about = serializers.CharField(source="profile.about")
    phone_number = PhoneNumberField(source="profile.phone_number")
    online = serializers.BooleanField(source="profile.online")

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "online",
            "last_login",
            "gender",
            "about",
            "phone_number",
            "profile_picture",
            "is_active",
        ]


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, "OLD_PASSWORD_FIELD_ENABLED", False
        )
        self.logout_on_password_change = getattr(
            settings, "LOGOUT_ON_PASSWORD_CHANGE", False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        self.request = self.context.get("request")
        self.user = getattr(self.request, "user", None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value),
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError("Invalid password")
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        old_password_match = (
            self.user,
            attrs["old_password"] == attrs["new_password1"],
        )

        if all(old_password_match):
            raise serializers.ValidationError(
                "your new password matching with old password"
            )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash

            update_session_auth_hash(self.request, self.user)


class UserMiniSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source="profile.profile_picture")
    gender = serializers.CharField(source="profile.gender")
    phone_number = PhoneNumberField(source="profile.phone_number")

    class Meta:
        model = get_user_model()
        fields = ["username", "profile_picture", "gender", "phone_number"]


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = "modified"


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ["primary", "user"]


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ["name", "codename", "content_type"]


class UserPermissionretriveSerializer(serializers.ModelSerializer):
    user_permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = UserModel
        fields = ("user_permissions",)


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("user_permissions",)


class NationalIDImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NationalIDImage
        fields = ("user", "image",)