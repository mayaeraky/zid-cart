import pytest
from cart.services import customers_service
from cart.models import Customer

@pytest.mark.django_db
def test_find_or_create_returns_existing_customer(shop, customer):
    data = {"name": "John Doe", "email": "john@example.com", "phone": "0123456789"}
    result = customers_service.find_or_create(shop, data)
    assert result.id == customer.id
    assert Customer.objects.count() == 1

@pytest.mark.django_db
def test_find_or_create_creates_new_customer(shop):
    data = {"name": "Alice", "email": "alice@example.com", "phone": "000"}
    result = customers_service.find_or_create(shop, data)
    assert result.email == "alice@example.com"
    assert Customer.objects.count() == 1
