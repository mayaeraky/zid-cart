from rest_framework import serializers
from cart.models import Purchase
from .purchase_products_serializer import PurchaseProductSerializer, PurchaseProductInputSerializer
from .coupons_serializer import CouponSerializer
from .addresses_serializer import AddressSerializer, CreateAddressSerializer
from .customers_serializer import CustomerSerializer, CreateCustomerSerializer
from .payments_serializer import PaymentSerializer

class PurchaseSerializer(serializers.ModelSerializer):
    products = PurchaseProductSerializer(source='purchase_products', many=True, read_only=True)
    coupon = CouponSerializer(read_only=True)
    address = AddressSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    payment = PaymentSerializer(source='payments', many=True, read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id',
            'customer',
            'total_amount',
            'status',
            'products',
            'coupon',
            'address',
            'payment'
        ]

class CreatePurchaseSerializer(serializers.Serializer):
    product = PurchaseProductInputSerializer()
    
class UpdatePurchaseSerializer(serializers.Serializer):
    customer = CreateCustomerSerializer(required=False)
    address = CreateAddressSerializer(required=False)
    status = serializers.ChoiceField(choices=Purchase.STATUS_CHOICES, required=False)
