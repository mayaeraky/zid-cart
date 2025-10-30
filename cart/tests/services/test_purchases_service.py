import pytest
from django.core.exceptions import ValidationError
from unittest.mock import patch
from cart.services import purchases_service
from cart.models import Purchase, PurchaseProduct, Payment

@pytest.mark.django_db
def test_create_purchase_and_attach_product(shop, customer, address, product):
    data = {
        "product": {
            "product_id": product.id,
            "quantity": 2
        }
    }
    purchase = purchases_service.create(shop, data)
    assert isinstance(purchase, Purchase)
    # product attached
    assert purchase.purchase_products.exists()
    pp = purchase.purchase_products.first()
    assert pp.product_id == product.id
    assert pp.quantity == 2

@pytest.mark.django_db
def test_update_one_attaches_customer_and_address(shop, product):
    # create initial purchase without customer
    purchase = Purchase.objects.create(shop=shop, status="draft")
    customer_data = {"name": "Alice", "email": "alice@example.com", "phone": "1"}
    address_data = {
        "line1": "L1", "city": "C", "region":"R", "country":"Country", "postal_code":"000"
    }
    updated = purchases_service.update_one(purchase, {"customer": customer_data, "address": address_data})
    assert updated.customer is not None
    assert updated.address is not None

@pytest.mark.django_db
def test_apply_and_remove_coupon(shop, purchase):
    # create coupon
    coupon = shop.coupons.create(code="FIRST", discount_type="percent", discount_value=10, is_active=True)
    # apply
    updated = purchases_service.apply_coupon(purchase, "FIRST")
    assert updated.coupon is not None
    # remove
    updated = purchases_service.remove_coupon(purchase)
    assert updated.coupon is None

@pytest.mark.django_db
def test_initialize_payment_creates_payment_record(shop, customer, address, product, payment_setup):
    # set purchase_product, address, and customer to purchase so that the validation passes
    purchase = Purchase.objects.create(shop=shop, customer=customer, address=address, status="draft")
    pp = purchase.purchase_products.create(product=product, quantity=2, price_at_purchase=product.price)

    spm = payment_setup["shop_payment_method"]

    with patch("cart.services.payments_service.loader.get_gateway") as mock_get_gateway:
        mock_gateway = mock_get_gateway.return_value
        mock_gateway.initialize_payment.return_value = "transaction_reference"

        result = purchases_service.initialize_payment(purchase, spm.id)
        assert result["success"] is True

        # ensure a pending payment exists or updated
        payment = Payment.objects.filter(purchase=purchase, status="pending").first()
        assert payment is not None
        assert payment.transaction_reference == "transaction_reference"

@pytest.mark.django_db
def test_activate_purchase_decrements_stock_and_sets_active(shop, customer, address, product):
    # create purchase with a product
    purchase = Purchase.objects.create(shop=shop, customer=customer, address=address, status="draft")
    pp = purchase.purchase_products.create(product=product, quantity=2, price_at_purchase=product.price)
    product_stock_before = product.stock

    purchases_service.activate(purchase)
    product.refresh_from_db()
    purchase.refresh_from_db()
    
    assert product.stock == product_stock_before - 2
    assert purchase.status == "active"
