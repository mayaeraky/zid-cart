from django.contrib import admin

# Register your models here.
from .models import Shop, Customer, Product, Coupon, Purchase, PurchaseProduct, PaymentGateway, PaymentMethod, Payment, Address, GatewayPaymentMethod, ShopPaymentMethod

admin.site.register([Shop, Customer, Product, Coupon, Purchase, PurchaseProduct, PaymentGateway, PaymentMethod, GatewayPaymentMethod, ShopPaymentMethod, Payment, Address])
