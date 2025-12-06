from django.urls import path
# from .views import TrendingProductsAPIView, RecommendedProductsAPIView
from . import views

urlpatterns = [
    # path("trending/", TrendingProductsAPIView.as_view(), name="trending"),
    # path("<int:product_id>/recommended/", RecommendedProductsAPIView.as_view(), name="recommended"),
     path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('products/trending/', views.trending_products, name='trending_products'),
    path('products/<int:pk>/recommended/', views.recommended_products, name='recommended_products'),
]
