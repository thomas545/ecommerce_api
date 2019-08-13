from rest_framework import serializers
from .models import Profile, Address
from drf_extra_fields.fields import Base64ImageField
from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField

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

