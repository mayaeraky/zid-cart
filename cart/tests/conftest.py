import pytest
from cart.models import Shop, Customer, Product, Purchase, Address, Coupon, PaymentGateway, PaymentMethod, GatewayPaymentMethod, ShopPaymentMethod

@pytest.fixture
def shop(db):
    return Shop.objects.create(name="Test Shop", domain="testshop.local")

@pytest.fixture
def customer(shop):
    return shop.customers.create(name="John Doe", email="john@example.com", phone="0123456789")

@pytest.fixture
def address(customer):
    return customer.addresses.create(
        line1="123 Test St",
        line2="",
        city="Cairo",
        region="Cairo",
        country="Egypt",
        postal_code="12345"
    )

@pytest.fixture
def product(shop):
    return shop.products.create(
        name="Product A",
        sku="SKU-A",
        price=100.00,
        stock=10,
        is_active=True
    )

@pytest.fixture
def purchase(shop, customer, address):
    return Purchase.objects.create(shop=shop, customer=customer, address=address, status="draft", total_amount=0)

@pytest.fixture
def payment_setup(shop):
    pg = PaymentGateway.objects.create(name="Stripe")
    pm = PaymentMethod.objects.create(name="Card", type="card")
    gpm = GatewayPaymentMethod.objects.create(gateway=pg, payment_method=pm)
    spm = ShopPaymentMethod.objects.create(shop=shop, gateway_payment_method=gpm, config={"api_key": "sk_test"}, is_active=True)
    return {"gateway": pg, "method": pm, "gateway_method": gpm, "shop_payment_method": spm}
