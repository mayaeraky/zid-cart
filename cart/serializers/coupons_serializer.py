from rest_framework import serializers
from cart.models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code', 'discount_type', 'discount_value', 'min_cart_value', 'is_active', 'valid_from', 'valid_to', 'once_per_customer']
