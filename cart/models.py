from django.db import models


class Shop(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Customer(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["shop", "email"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.shop.name})"

class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses', db_index=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.line1}, {self.city}, {self.country}"

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["shop", "sku"]),
            models.Index(fields=["shop", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.shop.name})"

class Coupon(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="coupons")
    code = models.CharField(max_length=50)
    discount_type = models.CharField(max_length=20, choices=[("percent", "Percent"), ("fixed", "Fixed Amount")])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_cart_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    once_per_customer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("shop", "code")
        indexes = [
            models.Index(fields=["shop", "is_active"]),
        ]

    def __str__(self):
        return f"{self.code} ({self.shop.name})"

class Purchase(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("shipped", "Shipped"),
        ("cancelled", "Cancelled"),
        ("delivered", "Delivered"),
    ]

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="purchases", db_index=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name="purchases", db_index=True)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases', db_index=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft", db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["shop", "status"]),
            models.Index(fields=["shop", "customer"]),
            models.Index(fields=["shop", "created_at"]),
        ]

    def __str__(self):
        return f"Purchase #{self.id} - {self.shop.name}"


class PurchaseProduct(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchase_products", db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, db_index=True)
    quantity = models.PositiveIntegerField(default=1)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["purchase", "product"]),
        ]

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

class PaymentGateway(models.Model):
    name = models.CharField(max_length=100)
    config = models.JSONField(default=dict, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GatewayPaymentMethod(models.Model):
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE, related_name="payment_methods", db_index=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name="payment_gateways", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("gateway", "payment_method")

    def __str__(self):
        return f"{self.gateway.name} - {self.payment_method.name}"


class ShopPaymentMethod(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="payment_methods", db_index=True)
    gateway_payment_method = models.ForeignKey(GatewayPaymentMethod, on_delete=models.CASCADE, related_name="shop_payment_methods", db_index=True)
    config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("shop", "gateway_payment_method")

    def __str__(self):
        return f"{self.shop.name}: {self.gateway_payment_method}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="payments", db_index=True)
    shop_payment_method = models.ForeignKey(ShopPaymentMethod, on_delete=models.PROTECT, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unpaid", db_index=True)
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["purchase", "status"]),
            models.Index(fields=["status", "transaction_reference"]),
        ]

    def __str__(self):
        return f"Payment #{self.id} - {self.status}"
