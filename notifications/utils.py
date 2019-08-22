from fcm_django.models import FCMDevice
from .serializers import NotificationSerializer


def push_notifications(user, title, body):
    data = {
        'user': user,
        'title': title,
        'body': body
    }

    serializer = NotificationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user)
    devices = FCMDevice.objects.filter(user=user)
    devices.send_message(title=title, body=body)