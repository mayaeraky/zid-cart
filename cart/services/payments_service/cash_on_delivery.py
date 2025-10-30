from .base import BasePaymentGateway

class CashOnDeliveryGateway(BasePaymentGateway):
    def initialize_payment(self, purchase, payment_method):
        # No API calls, just mark payment as pending
        return 

    def handle_webhook(self, purchase, data):
        # No webhooks for COD
        pass
