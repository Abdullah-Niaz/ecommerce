from rest_framework import serializers
from catalog.models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title','parent']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = Product
        fields = ['id','title','slug','description','price','brand','category','stock','rating','image','created_at']
