from rest_framework.routers import DefaultRouter
from .views.purchases_view import PurchaseViewSet
from .views.purchase_products_view import PurchaseProductViewSet
from .views.customers_view import CustomerViewSet
from .views.addresses_view import AddressViewSet

router = DefaultRouter()
router.register(r'purchases', PurchaseViewSet, basename='purchases')
router.register(r'purchase_products', PurchaseProductViewSet, basename='purchase_products')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'addresses', AddressViewSet, basename='addresses')

urlpatterns = router.urls
