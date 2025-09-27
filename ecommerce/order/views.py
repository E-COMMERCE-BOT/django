from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Status, DeliveryType, Order, OrderItem
from .serializers import StatusSerializer, DeliveryTypeSerializer, OrderSerializer
from user.models import User

class StatusViewSet(viewsets.ModelViewSet):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    lookup_field = 'id'

class DeliveryTypeViewSet(viewsets.ModelViewSet):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer
    lookup_field = 'id'

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    lookup_field = 'id'

    def get_queryset(self):
        user_id = self.request.query_params.get('user_id')
        if user_id:
            return Order.objects.filter(user__id=user_id)
        return super().get_queryset()
    
    def create(self, request, *args, **kwargs):
        tg_id = request.data.get("user_id")
        if not tg_id:
            return Response({"error": "user_id required"}, status=400)

        user, _ = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={"name": f"tg_{tg_id}"}
        )

        data = request.data.copy()
        data["user"] = user.id  

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        if order.status.name != "Cart":
            for item in order.items.all():
                item.product.stock -= item.quantity
                item.product.save()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    
    @action(detail=False, methods=["get"])
    def cart(self, request):
        tg_id = request.query_params.get("user_id")
        if not tg_id:
            return Response({"error": "user_id required"}, status=400)

        user, _ = User.objects.get_or_create(
            tg_id=tg_id,
            defaults={"name": f"tg_{tg_id}"}
        )

        cart_status, _ = Status.objects.get_or_create(name="Cart")
        cart, _ = Order.objects.get_or_create(user=user, status=cart_status)
        return Response(OrderSerializer(cart).data)

    @action(detail=True, methods=["post"])
    def add_item(self, request, id=None):
        order = self.get_object()
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id required"}, status=400)

        try:
            item, created = OrderItem.objects.get_or_create(order=order, product_id=product_id)
            if created:
                item.quantity = max(1, quantity)
            else:
                item.quantity += max(1, quantity)
            item.save()
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        order.refresh_from_db()
        return Response(OrderSerializer(order).data, status=200)

    @action(detail=True, methods=["post"])
    def update_item(self, request, id=None):
        """
        Поддерживает два режима:
        - delta: инкремент/декремент (например, +1 или -1)
        - quantity: выставить абсолютное количество
        """
        order = self.get_object()
        product_id = request.data.get("product_id")
        delta = request.data.get("delta", None)
        quantity = request.data.get("quantity", None)

        if not product_id:
            return Response({"error": "product_id required"}, status=400)

        try:
            item = order.items.get(product_id=product_id)
        except OrderItem.DoesNotExist:
            return Response({"error": "item not found"}, status=404)

        try:
            if delta is not None:
                d = int(delta)
                new_q = item.quantity + d
            elif quantity is not None:
                new_q = int(quantity)
            else:
                return Response({"error": "delta or quantity required"}, status=400)
        except (TypeError, ValueError):
            return Response({"error": "invalid delta/quantity"}, status=400)

        if new_q <= 0:
            item.delete()
        else:
            item.quantity = new_q
            item.save()

        order.refresh_from_db()
        return Response(OrderSerializer(order).data, status=200)

    @action(detail=True, methods=["post"])
    def remove_item(self, request, id=None):
        order = self.get_object()
        product_id = request.data.get("product_id")
        order.items.filter(product_id=product_id).delete()
        return Response(OrderSerializer(order).data)
