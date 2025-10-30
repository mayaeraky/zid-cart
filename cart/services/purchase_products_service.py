# cart/services/purchases_service.py

from django.db import transaction
from django.utils import timezone
from cart.models import (
    Purchase, Product, PurchaseProduct
)
from django.core.exceptions import ValidationError


@transaction.atomic
def create(data):
    """
    Creates a new purchase product and set its price at purchase.
    """
    purchase = Purchase.objects.get(id=data["purchase_id"])
    if purchase.status == "active":
        raise ValidationError(f"Cannot add products to an active purchase.") 

    product = Product.objects.get(id=data["product_id"])
    if product.stock < data["quantity"]:
        raise ValidationError(f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {data['quantity']}")


    purchase_product = PurchaseProduct.objects.filter(
        purchase_id=data["purchase_id"],
        product_id=data["product_id"]
    ).first()
    
    if purchase_product:
        purchase_product.quantity += data["quantity"]
    else:
        price_at_purchase = data["price_at_purchase"] if "price_at_purchase" in data else Product.objects.get(id=data["product_id"]).price
        purchase_product = PurchaseProduct.objects.create(
            purchase_id=data["purchase_id"],
            product_id=data["product_id"],
            quantity=data["quantity"],
            price_at_purchase=price_at_purchase
        )

    purchase_product.save() # this should trigger the signal to recalculate purchase total
    return purchase_product

def update_one(purchase_product, data):
    """
    Update purchase product details like quantity and price at purchase.
    """
   
    purchase = purchase_product.purchase
    if purchase.status == "active":
        raise ValidationError(f"Cannot edit products in an active purchase.") 

    product = purchase_product.product
    if product.stock < data["quantity"]:
        raise ValidationError(f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {data['quantity']}")
        
    for field, value in data.items():
        setattr(purchase_product, field, value)

    purchase_product.save()  # this should trigger the signal to recalculate purchase total
    return purchase_product

def delete_one(purchase_product):
    """
    Deletes a purchase product.
    """
    purchase = purchase_product.purchase
    if purchase.status == "active":
        raise ValidationError(f"Cannot delete products from an active purchase.") 

    purchase_product.delete()  # this should trigger the signal to recalculate purchase total

