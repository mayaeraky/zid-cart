from django.utils import timezone
from cart.models import Coupon, Purchase, PurchaseProduct
from django.core.exceptions import ValidationError

def validate(purchase, coupon_code):
    coupon = Coupon.objects.filter(shop=purchase.shop, code=coupon_code, is_active=True).first()

    if not coupon:
        raise ValidationError("Invalid or inactive coupon.")

    now = timezone.now().date()
    if coupon.valid_from and coupon.valid_from > now or coupon.valid_to and coupon.valid_to < now:
        raise ValidationError("Coupon expired.")

    purchase_products = purchase.purchase_products.all()
    subtotal = subtotal = sum(pp.quantity * pp.price_at_purchase for pp in purchase_products)
    if coupon.min_cart_value and subtotal < coupon.min_cart_value:
        raise ValidationError("Cart total below minimum for this coupon.") 

    if coupon.once_per_customer and purchase.customer:
        previous_uses = Purchase.objects.filter(
            shop=purchase.shop,
            customer=purchase.customer,
            coupon=coupon,
            status='active'
        ).exclude(id=purchase.id).exists()
        if previous_uses:
            raise ValidationError("Coupon can only be used once per customer.")
    return True
