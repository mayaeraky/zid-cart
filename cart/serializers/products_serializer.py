from rest_framework import serializers
from cart.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'stock', 'is_active']
