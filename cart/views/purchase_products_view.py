# cart/views/purchase_views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from cart.models import PurchaseProduct
from cart.serializers import (
    PurchaseProductSerializer,
    UpdatePurchaseProductSerializer,
    CreatePurchaseProductSerializer,
)
from cart.services.purchase_products_service import (
    create,
    update_one,
    delete_one
)
from django.core.exceptions import ValidationError

class PurchaseProductViewSet(viewsets.ModelViewSet):
    """
    Handles actions on purchase products.
    """

    serializer_class = PurchaseProductSerializer

    def get_queryset(self):
        shop = getattr(self.request, "shop", None)
        if not shop:
            return PurchaseProduct.objects.none()
        
        # Scope to only products that belong to this shop
        return PurchaseProduct.objects.filter(product__shop=shop)

    def get_serializer_class(self):
        """Dynamically choose serializer depending on the action."""
        if self.action == "create":
            return CreatePurchaseProductSerializer
        elif self.action == "update":
            return UpdatePurchaseProductSerializer
        return PurchaseProductSerializer

    def create(self, request, *args, **kwargs):
        """Creates a new purchase for the current shop."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try: 
            purchase_product = create(serializer.validated_data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = PurchaseProductSerializer(purchase_product)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Updates purchase product quantity or price at purchase."""
        purchase_product = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            updated_purchase_product = update_one(purchase_product, serializer.validated_data)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = PurchaseProductSerializer(updated_purchase_product)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Deletes a purchase product."""
        purchase_product = self.get_object()
        try:
            delete_one(purchase_product)
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)