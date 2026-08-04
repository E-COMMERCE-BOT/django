from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import DeliveryType, Order, OrderStatus
from .serializers import DeliveryTypeSerializer, OrderSerializer
from .services import (
    add_item,
    checkout,
    get_or_create_cart,
    remove_item,
    update_item,
)


class DeliveryTypeViewSet(viewsets.ModelViewSet):
    queryset = DeliveryType.objects.all()
    serializer_class = DeliveryTypeSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = (
        Order.objects.select_related("user", "delivery_type")
        .prefetch_related("items__product__category")
    )
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tg_id = self.request.query_params.get("tg_id")
        if tg_id:
            queryset = queryset.filter(user__tg_id=tg_id)
        return queryset

    @action(detail=False, methods=("get",))
    def cart(self, request):
        tg_id = request.query_params.get("tg_id")
        if not tg_id:
            return Response(
                {"detail": "tg_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart = get_or_create_cart(tg_id=int(tg_id))
        return Response(self.get_serializer(cart).data)

    @action(detail=True, methods=("post",))
    def add_item(self, request, pk=None):
        order = add_item(
            order=self.get_object(),
            product_id=int(request.data["product_id"]),
            quantity=int(request.data.get("quantity", 1)),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=("post",))
    def update_item(self, request, pk=None):
        order = update_item(
            order=self.get_object(),
            product_id=int(request.data["product_id"]),
            quantity=int(request.data["quantity"]),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=("post",))
    def remove_item(self, request, pk=None):
        order = remove_item(
            order=self.get_object(),
            product_id=int(request.data["product_id"]),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=("post",))
    def checkout(self, request, pk=None):
        order = checkout(
            order=self.get_object(),
            delivery_id=int(request.data["delivery_id"]),
        )
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=("post",))
    def set_status(self, request, pk=None):
        order = self.get_object()
        requested_status = request.data.get("status")
        valid_statuses = {value for value, _ in OrderStatus.choices}

        if requested_status not in valid_statuses:
            return Response(
                {"detail": "Invalid order status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = requested_status
        order.save(update_fields=("status",))
        return Response(self.get_serializer(order).data)
