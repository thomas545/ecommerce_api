from django.urls import path
from . import views


urlpatterns = [
    path("checkout/<int:pk>/", views.CheckoutView.as_view()),
    path("cart/checkout/<int:pk>/", views.CheckoutCartView.as_view()),
]
