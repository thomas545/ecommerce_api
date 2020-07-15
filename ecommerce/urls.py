from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_jwt.views import (
    obtain_jwt_token,
    refresh_jwt_token,
    verify_jwt_token,
)
from rest_framework.routers import DefaultRouter
from fcm_django.api.rest_framework import (
    FCMDeviceAuthorizedViewSet,
)  # this package for push notifications and messages


router = DefaultRouter()
router.register(r"devices", FCMDeviceAuthorizedViewSet)


urlpatterns = [
    path("jet/", include("jet.urls", "jet")),
    path("jet/dashboard/", include("jet.dashboard.urls", "jet-dashboard")),
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("", include("products.urls")),
    path("", include("user_profile.urls")),
    path("", include("cart.urls")),
    path("", include("notifications.urls")),
    path("", include("order.urls")),
    path("", include("checkout.urls")),
    path("", include("chat.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)),] + urlpatterns

