from django.shortcuts import render

# Create your views here.


from django.shortcuts import render, get_object_or_404
from .models import Product
from .services.recommendation_service import RecommendationService

def product_list(request):
    products = Product.objects.all()
    return render(request, "catalog/product_list.html", {"products": products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "catalog/product_detail.html", {"product": product})

def trending_products(request):
    trending = RecommendationService.get_trending()
    return render(request, "catalog/trending.html", {"trending": trending})

def recommended_products(request, pk):
    recommended = RecommendationService.get_recommended(pk)
    return render(request, "catalog/recommended.html", {"recommended": recommended})
