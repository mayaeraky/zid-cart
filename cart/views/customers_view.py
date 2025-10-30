from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from cart.models import Customer
from cart.serializers import CustomerSerializer, CreateCustomerSerializer

from cart.services.customers_service import (
    find_or_create,
)

class CustomerViewSet(viewsets.ModelViewSet):
    """
    Handles actions on customers.
    """

    serializer_class = CustomerSerializer

    def get_queryset(self):
        shop = getattr(self.request, "shop", None)
        if not shop:
            return Customer.objects.none()
        
        # Scope to only customers that belong to this shop
        return Customer.objects.filter(shop=shop)

    def get_serializer_class(self):
        """Dynamically choose serializer depending on the action."""
        if self.action == "create":
            return CreateCustomerSerializer
        return CustomerSerializer

    def create(self, request, *args, **kwargs):
        """find or Creates a customer for the current shop."""
        shop = getattr(request, "shop", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer = find_or_create(shop, serializer.validated_data)
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)