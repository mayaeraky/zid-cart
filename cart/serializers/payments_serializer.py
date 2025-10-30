from rest_framework import serializers
from cart.models import PaymentGateway, PaymentMethod, Payment, ShopPaymentMethod, GatewayPaymentMethod

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name', 'config', 'is_active']

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'is_active']

class GatewayPaymentMethodSerializer(serializers.ModelSerializer):
    gateway = PaymentGatewaySerializer(read_only=True)
    payment_method = PaymentMethodSerializer(read_only=True)

    class Meta:
        model = GatewayPaymentMethod
        fields = ['gateway', 'payment_method']


class ShopPaymentMethodSerializer(serializers.ModelSerializer):
    gateway_payment_method = GatewayPaymentMethodSerializer(read_only=True)
    class Meta:
        model = ShopPaymentMethod
        fields = ['gateway_payment_method']


class PaymentSerializer(serializers.ModelSerializer):
    method = ShopPaymentMethodSerializer(source='shop_payment_method', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'purchase_id', 'method', 'status', 'transaction_reference', 'created_at']
