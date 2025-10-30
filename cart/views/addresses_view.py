from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from cart.models import Address
from cart.serializers import AddressSerializer, CreateAddressSerializer

from cart.services.addresses_service import (
    create,
)

class AddressViewSet(viewsets.ModelViewSet):
    """
    Handles actions on addresses.
    """

    serializer_class = AddressSerializer

    def get_queryset(self):
        shop = getattr(self.request, "shop", None)
        if not shop:
            return Address.objects.none()
        
        # Scope to only addresses of customers that belong to current shop
        return Address.objects.filter(customer__shop=shop)

    def get_serializer_class(self):
        """Dynamically choose serializer depending on the action."""
        if self.action == "create":
            return CreateAddressSerializer
        return AddressSerializer

    def create(self, request, *args, **kwargs):
        """find or Creates a customer for the current shop."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
 
        address = create(serializer.validated_data)
        response_serializer = AddressSerializer(address)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)