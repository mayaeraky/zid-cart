from rest_framework import serializers
from cart.models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['line1', 'line2', 'city', 'region', 'country', 'postal_code']

class CreateAddressSerializer(serializers.Serializer):
    line1 = serializers.CharField()
    line2 = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField()
    region = serializers.CharField()
    country = serializers.CharField()
    postal_code = serializers.CharField(required=False, allow_blank=True)
    customer_id = serializers.IntegerField(required=False)
