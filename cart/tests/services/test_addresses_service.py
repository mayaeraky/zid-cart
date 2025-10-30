import pytest
from cart.services import addresses_service
from cart.models import Address

@pytest.mark.django_db
def test_create_address_success(customer):
    data = {
        "customer": customer,
        "line1": "123 Main St",
        "line2": "",
        "city": "Cairo",
        "region": "Cairo",
        "country": "Egypt",
        "postal_code": "12345"
    }
    address = addresses_service.create(data)
    assert isinstance(address, Address)
    assert address.customer == customer
    assert address.city == "Cairo"
