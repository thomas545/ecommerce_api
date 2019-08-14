from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework_jwt.views import verify_jwt_token



urlpatterns = [
    path('admin/', admin.site.urls),
    # path('create-token/', obtain_jwt_token),
    # path('refresh-token/', refresh_jwt_token),
    # path('verify-token/', verify_jwt_token),



    path('', include('products.urls')),
    path('', include('user_profile.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
