from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OrderItem, PurchaseLog
from .services.recommendation_service import RecommendationService

@receiver(post_save, sender=OrderItem)
def on_order_item_saved(sender, instance: OrderItem, created, **kwargs):
    if not created:
        return
    PurchaseLog.objects.create(
        user=instance.order.user if instance.order else None,
        product=instance.product,
        quantity=instance.quantity,
        order=instance.order
    )
    RecommendationService.increment_cooccurrence_for_order(instance.order)
