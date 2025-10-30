from django.core.management.base import BaseCommand
from cart.models import (
    Shop, Product, Coupon, Customer, Address,
    PaymentGateway, PaymentMethod,
    GatewayPaymentMethod, ShopPaymentMethod
)

class Command(BaseCommand):
    help = "Seeds the database with initial data for testing and development"

    def handle(self, *args, **options):
        # Delete old data
        Shop.objects.all().delete()
        Customer.objects.all().delete()
        Product.objects.all().delete()
        Coupon.objects.all().delete()
        PaymentGateway.objects.all().delete()
        PaymentMethod.objects.all().delete()

        # Create a shop
        shop = Shop.objects.create(name="Demo Shop", domain="demo-shop.com")

        # Create a customer
        customer = Customer.objects.create(
            shop=shop, name="Maya Eraky", email="maya@gmail.com", phone="1234567890"
        )

        # Create an Address
        Address.objects.create(
            customer=customer,
            shop=shop,
            line1="1 street",
            line2="Apartment 2",
            city="Cairo",
            region="5th Settlement",
            country="Egypt",
            postal_code="12345",
            is_default=True
        )

        # Create a product
        Product.objects.create(shop=shop, name="T-shirt", sku="p1", price=850, stock=10, is_active=True)
        Product.objects.create(shop=shop, name="Dress", sku="p2", price=999.99, stock=20, is_active=True)
        Product.objects.create(shop=shop, name="Skirt", sku="p3", price=250.99, stock=30, is_active=True)

        # Create a coupon
        coupon = Coupon.objects.create(
            shop=shop,
            code="FIRST10",
            discount_type="percentage",
            discount_value=10,
            min_cart_value=300,
            is_active=True,
            valid_from="2025-01-01",
            valid_to="2025-12-31"
        )

        # Create payment gateways
        stripe = PaymentGateway.objects.create(name="Stripe", config={"api_key": "api_key1"}, is_active=True)
        cod = PaymentGateway.objects.create(name="Cash on Delivery", config={}, is_active=True)

        # Create global Payment Methods
        card = PaymentMethod.objects.create(name="Credit Card", type="card", is_active=True)
        cash = PaymentMethod.objects.create(name="Cash on Delivery", type="cod", is_active=True)

        # Link gateways to methods
        gateway_card = GatewayPaymentMethod.objects.create(gateway=stripe, payment_method=card)
        gateway_cash = GatewayPaymentMethod.objects.create(gateway=cod, payment_method=cash)

        # Link gateway payment methods to the shop
        ShopPaymentMethod.objects.create(shop=shop, gateway_payment_method=gateway_card, config={}, is_active=True)
        ShopPaymentMethod.objects.create(shop=shop, gateway_payment_method=gateway_cash, config={}, is_active=True)

        self.stdout.write(self.style.SUCCESS("data created successfully!"))
