import pytest
from django.core.exceptions import ValidationError
from cart.services import purchase_products_service
from cart.models import PurchaseProduct

@pytest.mark.django_db
def test_create_purchase_product_success(purchase, product):
    data = {
        "purchase_id": purchase.id,
        "product_id": product.id,
        "quantity": 2
    }
    pp = purchase_products_service.create(data)
    assert isinstance(pp, PurchaseProduct)
    assert pp.purchase_id == purchase.id
    assert pp.product_id == product.id
    assert pp.quantity == 2
    assert float(pp.price_at_purchase) == float(product.price)

@pytest.mark.django_db
def test_create_purchase_product_insufficient_stock(purchase, product):
    data = {
        "purchase_id": purchase.id,
        "product_id": product.id,
        "quantity": 9999
    }
    with pytest.raises(ValidationError):
        purchase_products_service.create(data)

@pytest.mark.django_db
def test_create_purchase_product_blocked_if_purchase_active(purchase, product):
    purchase.status = "active"
    purchase.save()
    data = {
        "purchase_id": purchase.id,
        "product_id": product.id,
        "quantity": 1
    }
    with pytest.raises(ValidationError):
        purchase_products_service.create(data)

@pytest.mark.django_db
def test_update_one_changes_fields(purchase, product):
    pp = purchase.purchase_products.create(product=product, quantity=1, price_at_purchase=product.price)
    data = {"quantity": 3, "price_at_purchase": 150}
    updated = purchase_products_service.update_one(pp, data)
    assert updated.quantity == 3
    assert float(updated.price_at_purchase) == 150.0

@pytest.mark.django_db
def test_delete_one_removes(purchase, product):
    pp = purchase.purchase_products.create(product=product, quantity=1, price_at_purchase=product.price)
    purchase_products_service.delete_one(pp)
    assert not PurchaseProduct.objects.filter(id=pp.id).exists()
