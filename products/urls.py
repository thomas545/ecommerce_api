from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
router = DefaultRouter()

router.register(r'products',views.ProductDocumentView)

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
    path('category/', views.CategoryListAPIView.as_view()),
    path('category/<int:pk>/', views.CategoryAPIView.as_view()),
    path('list/product/', views.ListProductAPIView.as_view()),
    path('list-product/user/', views.ListUserProductAPIView.as_view()),
    path('create/product/', views.CreateProductAPIView.as_view()),
    path('product/<int:pk>/delete/', views.DestroyProductAPIView.as_view()),
    path('product/<int:pk>/', views.ProductDetailView.as_view()),
    path('product/views/', views.ProductViewsAPIView.as_view()),
]
