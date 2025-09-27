from rest_framework import routers
from .views import StatusViewSet, DeliveryTypeViewSet, OrderViewSet

order_router = routers.DefaultRouter()
order_router.register(r'statuses', StatusViewSet, basename='status')
order_router.register(r'deliveries', DeliveryTypeViewSet, basename='delivery')
order_router.register(r'orders', OrderViewSet, basename='order')