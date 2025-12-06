from django.conf import settings
from django.db import models
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    title = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='children')

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    brand = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    stock = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    image = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.pk} by {self.user}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

class PurchaseLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(Order, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=['product', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

class ProductRecommendation(models.Model):
    product = models.ForeignKey(Product, related_name='recommendations', on_delete=models.CASCADE)
    recommended_product = models.ForeignKey(Product, related_name='+', on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'recommended_product')
        indexes = [models.Index(fields=['product', '-score'])]
