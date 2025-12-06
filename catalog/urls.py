from django.urls import path
from .views import TrendingProductsAPIView, RecommendedProductsAPIView

urlpatterns = [
    path("trending/", TrendingProductsAPIView.as_view(), name="trending"),
    path("<int:product_id>/recommended/", RecommendedProductsAPIView.as_view(), name="recommended"),
]
