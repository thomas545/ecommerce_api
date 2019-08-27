from django.urls import path, include
from . import views
from django.views.generic import TemplateView
from rest_auth.views import (
                            LoginView, PasswordResetView, 
                            PasswordResetConfirmView, PasswordChangeView, 
                            LogoutView
                            )
from rest_auth.registration.views import RegisterView, VerifyEmailView



urlpatterns = [
    path('', include('rest_auth.urls')),
    path('registration/', views.RegisterAPIView.as_view(), name='account_signup'),
    path('registration/', include('rest_auth.registration.urls')),

    path('login/', LoginView.as_view(), name='account_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),

    path('password/reset/', PasswordResetView.as_view(), name='rest_password_reset'),

    path('password/reset/confirm/<str:uidb64>/<str:token>/', 
            PasswordResetConfirmView.as_view(), 
            name='rest_password_reset_confirm'),

    path('password/change/', PasswordChangeView.as_view(), name='rest_password_change'),

    path('account-confirm-email/sent/', TemplateView.as_view(), name='account_confirm_email'),
    path('account-confirm-email/<str:key>', VerifyEmailView.as_view(), name='rest_verify_email'),

    path('account-confirm-sms/sent/', views.SMSVerificationAPIView.as_view()),

    path('profile/<int:pk>/', views.ProfileAPIView.as_view()),
    path('user/<str:username>/', views.UserDetailView.as_view()),
    path('addresses/', views.ListAddressAPIView.as_view()),
    path('address/<int:pk>', views.AddressDetailView.as_view()),
    path('create/address/', views.createAddressAPIView.as_view()),

    path('facebook/', views.FacebookConnectView.as_view()),
    path('twitter/', views.TwitterConnectView.as_view()),

]
