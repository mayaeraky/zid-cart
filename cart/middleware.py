from cart.models import Shop
from django.http import Http404

class CurrentShopMiddleware:
    """Attach current Shop to request based on domain"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            return self.get_response(request)
            
        # remove port if found
        host = request.get_host().split(':')[0]
        try:
            request.shop = Shop.objects.get(domain=host)
        except Shop.DoesNotExist:
            raise Http404("Shop not found for this domain")
        response = self.get_response(request)
        return response
