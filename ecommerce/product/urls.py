from rest_framework import routers

from .views import CategoryViewSet, ProductViewSet

product_router = routers.DefaultRouter()
product_router.register(r'categories', CategoryViewSet, basename='category')
product_router.register(r'products', ProductViewSet, basename='product')
