from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

def find_or_create(shop, data):
    email = data["email"]
    customer = shop.customers.filter(email=email).first()
    if customer:
        for key, value in data.items():
            setattr(customer, key, value)
        customer.save()
        return customer
    customer = shop.customers.create(**data)
    return customer
   