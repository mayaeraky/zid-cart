from rest_framework import serializers
from cart.models import Customer
from cart.serializers.addresses_serializer import AddressSerializer

class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source='addresses', many=True, read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address']

class CreateCustomerSerializer(serializers.Serializer):
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
