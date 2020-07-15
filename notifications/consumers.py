from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["url_route"]["kwargs"]["username"]
        self.user_notification = "notification_%s" % self.user
        # self.user_notification = None
        # user = User.objects.filter(username=self.user)
        # if user:
        # self.user_notification = 'notification_%s' % user[0].id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.user_notification, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.user_notification, self.channel_name
        )

    # Receive message from WebSocket
    # you can do this out of consumers in function or class based views or signal or normal func
    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     notification = text_data_json['notification']

    #     # Send message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name,
    #         {
    #             'type': 'notifications',
    #             'notification': notification
    #         }
    #     )

    # Receive message from room group
    def push_notification(self, event):
        title = event["title"]
        body = event["body"]
        created = event["created"]
        status = event["status"]

        # Send message to WebSocket
        self.send(
            text_data=json.dumps(
                {"title": title, "body": body, "created": created, "status": status}
            )
        )

