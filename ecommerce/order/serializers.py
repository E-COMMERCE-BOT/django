from rest_framework import serializers

from .models import Status, DeliveryType, Order, OrderItem, Product, User
from user.serializers import UserSerializer
from product.serializers import ProductSerializer

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    status = StatusSerializer(read_only=True)
    status_id = serializers.PrimaryKeyRelatedField(
        queryset=Status.objects.all(), source='status', write_only=True, allow_null=False, required=True
    )
    delivery = DeliveryTypeSerializer(read_only=True)
    delivery_id = serializers.PrimaryKeyRelatedField(
        queryset=DeliveryType.objects.all(), source='delivery_type', write_only=True, allow_null=False, required=True
    )   
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_id', 'status', 'status_id', 'delivery', 'delivery_id', 'created_at', 'items', 'total']

    def get_total(self, obj):
        return obj.get_total()