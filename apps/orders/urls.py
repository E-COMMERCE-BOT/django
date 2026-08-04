from rest_framework.routers import DefaultRouter

from .views import DeliveryTypeViewSet, OrderViewSet

router = DefaultRouter()
router.register("deliveries", DeliveryTypeViewSet, basename="delivery")
router.register("", OrderViewSet, basename="order")

urlpatterns = router.urls
