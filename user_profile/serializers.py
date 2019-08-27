from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework.validators import UniqueValidator

from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .models import Profile, Address, SMSVerification


class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    birth_date = serializers.CharField(required=True, write_only=True)
    phone_number = PhoneNumberField(required=True, write_only=True, 
                                    validators = [UniqueValidator(
                                        queryset = Profile.objects.all(),
                                        message = _("A user is already registered with this phone number."))])

    def get_cleaned_data_profile(self):
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'birth_date': self.validated_data.get('birth_date', ''),
            'phone_number': self.validated_data.get('phone_number', '')
        }

    def create_profile(self, user, validated_data):
        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        user.save()

        user.profile.birth_date = self.validated_data.get('birth_date')
        user.profile.phone_number = self.validated_data.get('phone_number')
        user.profile.save()

    def custom_signup(self, request, user):
        self.create_profile(user, self.get_cleaned_data_profile()) 

class SMSVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSVerification
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username',read_only=True)
    gender = serializers.SerializerMethodField()
    profile_picture = Base64ImageField()

    def get_gender(self, obj):
        return obj.get_gender_display()

    class Meta:
        model = Profile
        fields = ['user', 'profile_picture', 'phone_number', 'gender', 'about']

        
class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(source='profile.profile_picture')
    gender = serializers.CharField(source='profile.gender')
    about = serializers.CharField(source='profile.about')
    phone_number = PhoneNumberField(source='profile.phone_number')

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'password',
                    'first_name', 'last_name', 
                    'last_login', 'gender', 'about', 
                    'phone_number', 'profile_picture', 'is_active']


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"


class CreateAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = ['primary', 'user']

