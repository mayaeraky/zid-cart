from django.db import transaction
from django.utils import timezone
from cart.models import Address

def create(data):
    address = Address.objects.create(**data)
    return address