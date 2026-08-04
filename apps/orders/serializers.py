from rest_framework import serializers

from apps.catalog.serializers import ProductSerializer
from apps.users.serializers import UserSerializer

from .models import DeliveryType, Order


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = ("id", "name", "description", "price")


class OrderItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    product = ProductSerializer()
    quantity = serializers.IntegerField()
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
    )


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    delivery = DeliveryTypeSerializer(
        source="delivery_type",
        read_only=True,
    )
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "user",
            "status",
            "delivery",
            "items",
            "total",
            "created_at",
        )
        read_only_fields = (
            "id",
            "number",
            "user",
            "items",
            "total",
            "created_at",
        )
