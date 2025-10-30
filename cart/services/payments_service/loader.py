from cart.models import ShopPaymentMethod

def get_gateway(shop_payment_method: ShopPaymentMethod):
    try:
        payment_gateway_name = shop_payment_method.gateway_payment_method.gateway.name.lower()
        config = shop_payment_method.config
        # Import module dynamically
        module = __import__(f"cart.services.payments_service.{payment_gateway_name}", fromlist=["*"])
        # Each module must define a class named <GatewayName>Gateway where GatewayName is converted to camel case
        camel_case_name = "".join(word.capitalize() for word in payment_gateway_name.split("_"))
        class_name = f"{camel_case_name}Gateway"
        gateway_class = getattr(module, class_name)
        gateway_instance = gateway_class()

        # Configure gateway if it has a configure() method
        if hasattr(gateway_instance, "configure"):
            gateway_instance.configure(config)

        return gateway_instance
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Unknown or misconfigured gateway: {payment_gateway_name}") from e
