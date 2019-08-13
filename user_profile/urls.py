from django.urls import path
from . import views

urlpatterns = [
    path('profile/<int:pk>/', views.ProfileAPIView.as_view()),
    path('user/<str:username>/', views.UserDetailView.as_view()),
    path('addresses/', views.ListAddressAPIView.as_view()),
    path('address/<int:pk>', views.AddressDetailView.as_view()),
    path('create/address/', views.createAddressAPIView.as_view()),

]
