from rest_framework import serializers
from fcm_django.models import FCMDevice
from .models import Notification


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = [
            "name",
            "active",
            "user",
            "device_id",
            "registration_id",
            "type",
            "date_created",
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["title", "body"]


class NotificationMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "title", "body", "status"]

