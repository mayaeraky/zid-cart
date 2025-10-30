# cart/services/purchases_service.py

from django.db import transaction
from django.utils import timezone
from cart.models import (
    Purchase, Product, PurchaseProduct, Coupon,
    PaymentMethod, Payment
)
from cart.services.purchase_products_service import create as create_purchase_product
from cart.services.customers_service import find_or_create as find_or_create_customer
from cart.services.addresses_service import create as create_address
from cart.services.coupons_service import validate as validate_coupon
from cart.services.payments_service.loader import get_gateway
from django.core.exceptions import ValidationError


@transaction.atomic
def create(shop, data):
    """
    Creates a new purchase for the given shop and links a purchase product to it.
    """
    purchase = Purchase.objects.create(
        shop=shop,
        status="draft",
    )
    purchase.save()
    
    product_data = data.get("product")
    purchase_product_data = {
        "product_id": product_data["product_id"],
        "purchase_id": purchase.id,
        "quantity": product_data["quantity"],
    }
    create_purchase_product(purchase_product_data)

    return purchase

@transaction.atomic
def update_one(purchase, data):
    """
    Update purchase details like customer, address, and status.
    """
    customer_id = handle_customer_attachment(purchase, data.get("customer"))
    
    handle_address_attachment(purchase, customer_id, data.get("address"))
    if data.get("status"):
        purchase.status = data["status"]
    
    purchase.save()
    return purchase

def handle_customer_attachment(purchase, customer_data):
    """
    Attach or create a customer for the purchase.
    """
    if not customer_data:
        return

    shop = purchase.shop
    customer = find_or_create_customer(shop, customer_data)

    purchase.customer = customer
    return customer.id

def handle_address_attachment(purchase, customer_id, address_data):
    """
    Attach or create an address for the purchase.
    """
    if not address_data:
        return

    address_data["customer_id"] = customer_id
    address = create_address(address_data)
    purchase.address = address

@transaction.atomic
def apply_coupon(purchase, coupon_code):
    """
    Apply a valid coupon to the purchase.
    """

    validate_coupon(purchase, coupon_code)
    coupon = Coupon.objects.get(shop=purchase.shop, code=coupon_code, is_active=True)
    purchase.coupon = coupon
    purchase.save() # will trigger total calculation via signal
    return purchase


@transaction.atomic
def remove_coupon(purchase):
    """
    Removes coupon from a purchase.
    """
    purchase.coupon = None
    purchase.save() # will trigger total calculation via signal
    return purchase

def calculate_total(purchase):
    """
    Utility function to calculate total purchase amount.
    """
    if purchase.status != "draft":
        return

    purchase_products = purchase.purchase_products.all()
    subtotal = sum(pp.quantity * pp.price_at_purchase for pp in purchase_products)
    discount = 0

    if purchase.coupon:
        coupon = purchase.coupon
        if coupon.discount_type == "percent":
            discount = subtotal * (coupon.discount_value / 100)
        elif coupon.discount_type == "fixed":
            discount = coupon.discount_value

    total_amount = max(subtotal - discount, 0)
    Purchase.objects.filter(pk=purchase.pk).update(total_amount=total_amount)
    purchase.refresh_from_db()  # Refresh the instance to get updated total_amount

def initialize_payment(purchase, shop_payment_method_id):
    """
    Utility function to initiate payment.
    """

    ## valiate purchase before online payment
    validate(purchase)

    shop_payment_method = purchase.shop.payment_methods.get(
        id=shop_payment_method_id
    )
    payment_gateway = get_gateway(shop_payment_method)

    payment_method = shop_payment_method.gateway_payment_method.payment_method
    transaction_reference = payment_gateway.initialize_payment(purchase, payment_method)

    payment = Payment.objects.filter(purchase=purchase, status="pending").first()

    if payment:
        payment.transaction_reference = transaction_reference
        payment.shop_payment_method = shop_payment_method
        payment.save()
    else:    
        payment = Payment.objects.create(
            status="pending",
            shop_payment_method=shop_payment_method,
            purchase=purchase,
            transaction_reference=transaction_reference,
        ) 
    return {"success": True, "message": "Payment was successfully initialized"}

def handle_payment_webhook(purchase, data):
    """
    Utility function to handle payment gateway webhooks.
    """
    payment = Payment.objects.get(purchase=purchase, status="pending")
    shop_payment_method = payment.shop_payment_method
    payment_gateway = get_gateway(shop_payment_method)

    success = payment_gateway.handle_webhook(purchase, data)
    if success:
        payment.status = "paid"
        activate(purchase)
    else:
        payment.status = "failed"

    payment.save()
    return {"success": success}

@transaction.atomic
def activate(purchase):
    """
    Finalizes purchase and creates a Payment record.
    """
    validate(purchase)
    
    for pp in purchase.purchase_products.all():
        product = pp.product
        product.stock -= pp.quantity
        product.save()

    purchase.status = "active"
    purchase.save()
    purchase.refresh_from_db()
    return purchase

def validate(purchase):
    """
    Validates that the purchase is ready to be activated.
    """
    if purchase.status != "draft":
        raise ValidationError("Only draft purchases can be activated.")

    if not purchase.customer:
        raise ValidationError("Purchase must have a customer before activation.")

    if not purchase.address:
        raise ValidationError("Purchase must have an address before activation.")

    if purchase.total_amount <= 0:
        raise ValidationError("Purchase total amount must be greater than zero.")
    
    for pp in purchase.purchase_products.all():
        product = pp.product
        if product.stock < pp.quantity:
            raise ValidationError(f"Product {pp.product.name} has insuffecient quantity.")

        if product.price != pp.price_at_purchase:
            pp.price_at_purchase = product.price
            pp.save()
            raise ValidationError(f"Product {pp.product.name} price has changed since added to purchase; price will be updated in the cart accordingly.")
    if purchase.coupon:
        validate_coupon(purchase, purchase.coupon.code)

        if purchase.updated_at < purchase.coupon.updated_at:
            purchase.save()
            raise ValidationError(f"Coupon has been modifed; please re-check your total amount before proceeding.")
 
