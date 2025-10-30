from rest_framework import serializers
from cart.models import PurchaseProduct
from .products_serializer import ProductSerializer

class PurchaseProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = PurchaseProduct
        fields = ['id', 'product', 'quantity', 'price_at_purchase']

class CreatePurchaseProductSerializer(serializers.Serializer):
    purchase_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    price_at_purchase = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

class UpdatePurchaseProductSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, required=False)
    price_at_purchase = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

class PurchaseProductInputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)