import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from cart.services import coupons_service

@pytest.mark.django_db
def test_validate_valid_coupon(shop, purchase):
    coupon = shop.coupons.create(
        code="SAVE10",
        discount_type="percent",
        discount_value=10,
        min_cart_value=0,
        valid_from=timezone.now().date(),
        valid_to=timezone.now().date(),
        is_active=True,
    )
    purchase.purchase_products.create(
        product=shop.products.create(name="P1", sku="P1", price=50, stock=10),
        quantity=2,
        price_at_purchase=50
    )
    assert coupons_service.validate(purchase, "SAVE10") is True

@pytest.mark.django_db
def test_validate_raises_for_inactive_coupon(shop, purchase):
    shop.coupons.create(code="OFF", discount_type="fixed", discount_value=5, is_active=False)
    with pytest.raises(ValidationError):
        coupons_service.validate(purchase, "OFF")

@pytest.mark.django_db
def test_validate_raises_for_expired_coupon(shop, purchase):
    yesterday = timezone.now().date().replace(day=timezone.now().day - 1)
    shop.coupons.create(
        code="OLD",
        discount_type="percent",
        discount_value=10,
        valid_to=yesterday,
        is_active=True
    )
    with pytest.raises(ValidationError):
        coupons_service.validate(purchase, "OLD")

@pytest.mark.django_db
def test_validate_raises_for_min_cart_value(shop, purchase):
    coupon = shop.coupons.create(
        code="BIGORDER",
        discount_type="fixed",
        discount_value=10,
        min_cart_value=500,
        is_active=True
    )
    purchase.purchase_products.create(
        product=shop.products.create(name="P1", sku="P1", price=50, stock=10),
        quantity=2,
        price_at_purchase=50
    )
    with pytest.raises(ValidationError):
        coupons_service.validate(purchase, "BIGORDER")
