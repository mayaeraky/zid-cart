class BasePaymentGateway:
    def initialize_payment(self, purchase: 'Purchase', payment_method: 'PaymentMethod'):
        raise NotImplementedError

    def handle_webhook(self, purchase, data):
        raise NotImplementedError
