import pytest
from unittest.mock import patch
from cart.models import Payment, Purchase
from cart.services.payments_service.loader import get_gateway

@pytest.mark.django_db
def test_cash_on_delivery_initialize_payment_creates_pending_payment(shop, customer, address, product, payment_setup):
    from cart.services.payments_service.cash_on_delivery import CashOnDeliveryGateway

    gateway = CashOnDeliveryGateway()
    shop_payment_method = payment_setup["shop_payment_method"]

    # patch loader.get_gateway to return our cash gateway
    with patch("cart.services.payments_service.loader.get_gateway", return_value=gateway):
        # set purchase_product, address, and customer to purchase so that the validation passes
        purchase = Purchase.objects.create(shop=shop, customer=customer, address=address, status="draft")
        pp = purchase.purchase_products.create(product=product, quantity=2, price_at_purchase=product.price)

        from cart.services import purchases_service
        result = purchases_service.initialize_payment(purchase, shop_payment_method.id)
        assert result["success"] is True
        assert Payment.objects.filter(purchase=purchase, status="pending").exists()

@pytest.mark.django_db
def test_stripe_initialize_payment_uses_gateway_mock(shop, customer, address, product, payment_setup):
    shop_payment_method = payment_setup["shop_payment_method"]
    with patch("cart.services.payments_service.loader.get_gateway") as mock_loader:
        mock_gateway = mock_loader.return_value
        mock_gateway.initialize_payment.return_value = "transaction_reference"

        from cart.services import purchases_service
        # set purchase_product, address, and customer to purchase so that the validation passes
        purchase = Purchase.objects.create(shop=shop, customer=customer, address=address, status="draft")
        pp = purchase.purchase_products.create(product=product, quantity=2, price_at_purchase=product.price)

        result = purchases_service.initialize_payment(purchase, shop_payment_method.id)
        assert result["success"] is True

        payment = Payment.objects.filter(purchase=purchase).first()
        assert payment.transaction_reference == "transaction_reference"
