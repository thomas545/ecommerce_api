from fcm_django.models import FCMDevice
from .serializers import NotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


def push_notifications(user, title, body):
    data = {"user": user, "title": title, "body": body}
    serializer = NotificationSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save(user=user)

    async_to_sync(channel_layer.group_send)(
        "Notification_" + str(user.id),
        {
            "type": "new notification",
            "title": title,
            "body": body,
            "created": str(serializer.data.get("created")),
            "status": str(serializer.data.get("status")),
        },
    )

    devices = FCMDevice.objects.filter(user=user)
    devices.send_message(title=title, body=body)
