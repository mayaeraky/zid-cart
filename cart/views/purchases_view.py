from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from cart.models import Purchase
from cart.serializers import (
    PurchaseSerializer,
    CreatePurchaseSerializer,
    UpdatePurchaseSerializer,
)
from cart.services.purchases_service import (
    create,
    update_one,
    apply_coupon,
    remove_coupon,
    initialize_payment,
    handle_payment_webhook,
    activate
)
from django.core.exceptions import ValidationError

class PurchaseViewSet(viewsets.ModelViewSet):
    """
    Handles listing, retrieving, creating, updating, and special actions on purchases.
    Automatically scoped to the current shop (from middleware).
    """

    serializer_class = PurchaseSerializer

    def get_queryset(self):
        shop = getattr(self.request, "shop", None)
        if not shop:
            return Purchase.objects.none()
        return (
            Purchase.objects.filter(shop=shop, status="draft").select_related('customer', 'coupon', 'address').prefetch_related('purchase_products')
        )

    def get_serializer_class(self):
        """Dynamically choose serializer depending on the action."""
        if self.action == "create":
            return CreatePurchaseSerializer
        elif self.action == "update":
            return UpdatePurchaseSerializer
        return PurchaseSerializer

    def create(self, request, *args, **kwargs):
        """Creates a new purchase for the current shop."""
        shop = getattr(request, "shop", None)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        purchase = create(shop, serializer.validated_data)
        response_serializer = PurchaseSerializer(purchase)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Updates purchase details — like customer, address, and status."""
        purchase = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_purchase = update_one(purchase, serializer.validated_data)
        response_serializer = PurchaseSerializer(updated_purchase)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def apply_coupon(self, request, pk=None):
        """Applies a coupon to the purchase."""
        purchase = self.get_object()
        coupon_code = request.data.get("coupon_code")
        try:
            updated_purchase = apply_coupon(purchase, coupon_code)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        response_serializer = PurchaseSerializer(updated_purchase)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def remove_coupon(self, request, pk=None):
        """Removes a coupon from the purchase."""
        purchase = self.get_object()
        updated_purchase = remove_coupon(purchase)
        response_serializer = PurchaseSerializer(updated_purchase)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def initialize_payment(self, request, pk=None):
        """Initiate payment for this purchase."""
        purchase = self.get_object()
        shop_payment_method_id = request.data.get("shop_payment_method_id")

        payment_result = initialize_payment(purchase, shop_payment_method_id)
        return Response(payment_result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def payment_webhook(self, request, pk=None):
        """Handle payment gateway webhook for this purchase."""
        purchase = self.get_object()
        webhook_data = request.data.get("webhook_data", {})

        webhook_result = handle_payment_webhook(purchase, webhook_data)
        return Response(webhook_result, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Handle activation of this purchase."""
        purchase = self.get_object()

        active_purchase = activate(purchase)
        response_serializer = PurchaseSerializer(active_purchase)
        return Response(response_serializer.data, status=status.HTTP_200_OK)