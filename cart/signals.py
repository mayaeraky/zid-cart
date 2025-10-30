from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from cart.models import Purchase, PurchaseProduct
from cart.services.purchases_service import calculate_total

@receiver(post_save, sender=Purchase)
def after_purchase_saved(sender, instance, **kwargs):
    calculate_total(instance)
    
@receiver(post_save, sender=PurchaseProduct)
def after_purchase_saved(sender, instance, **kwargs):
    calculate_total(instance.purchase)

@receiver(post_delete, sender=PurchaseProduct)
def after_purchase_product_deleted(sender, instance, **kwargs):
    calculate_total(instance.purchase)
