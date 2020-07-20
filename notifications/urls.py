from django.urls import path
from . import views


urlpatterns = [
    path("create-device/", views.CreateDeviceAPIView.as_view()),
    path("notifications/", views.NotificationListView.as_view()),
    path("notifications/<int:pk>/", views.NotificationAPIView.as_view()),
    path("mark-all-as-read/", views.MarkedAllAsReadNotificationView.as_view()),
]
