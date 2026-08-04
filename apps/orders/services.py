from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Product
from apps.users.models import User

from .models import DeliveryType, Order, OrderItem, OrderStatus


@transaction.atomic
def get_or_create_cart(*, tg_id: int) -> Order:
    user, _ = User.objects.get_or_create(tg_id=tg_id)
    cart, _ = Order.objects.get_or_create(
        user=user,
        status=OrderStatus.CART,
    )
    return cart


@transaction.atomic
def add_item(
    *,
    order: Order,
    product_id: int,
    quantity: int,
) -> Order:
    if order.status != OrderStatus.CART:
        raise ValidationError("Items can only be changed in a cart.")

    product = Product.objects.select_for_update().get(pk=product_id)
    quantity = max(quantity, 1)

    item, created = OrderItem.objects.get_or_create(
        order=order,
        product=product,
        defaults={"quantity": quantity},
    )
    if not created:
        item.quantity += quantity

    if item.quantity > product.stock:
        raise ValidationError(
            f"Only {product.stock} units are available."
        )

    item.save(update_fields=("quantity",))
    return order


@transaction.atomic
def update_item(
    *,
    order: Order,
    product_id: int,
    quantity: int,
) -> Order:
    if order.status != OrderStatus.CART:
        raise ValidationError("Items can only be changed in a cart.")

    item = OrderItem.objects.select_related("product").get(
        order=order,
        product_id=product_id,
    )

    if quantity <= 0:
        item.delete()
        return order

    if quantity > item.product.stock:
        raise ValidationError(
            f"Only {item.product.stock} units are available."
        )

    item.quantity = quantity
    item.save(update_fields=("quantity",))
    return order


@transaction.atomic
def remove_item(*, order: Order, product_id: int) -> Order:
    if order.status != OrderStatus.CART:
        raise ValidationError("Items can only be changed in a cart.")

    order.items.filter(product_id=product_id).delete()
    return order


@transaction.atomic
def checkout(*, order: Order, delivery_id: int) -> Order:
    if order.status != OrderStatus.CART:
        raise ValidationError("Only a cart can be checked out.")

    items = list(
        order.items.select_related("product").select_for_update()
    )
    if not items:
        raise ValidationError("The cart is empty.")

    for item in items:
        if item.quantity > item.product.stock:
            raise ValidationError(
                f"Not enough stock for {item.product.name}."
            )

    for item in items:
        item.product.stock -= item.quantity
        item.product.save(update_fields=("stock",))

    order.delivery_type = DeliveryType.objects.get(pk=delivery_id)
    order.status = OrderStatus.CREATED
    order.stock_reserved = True
    order.save(
        update_fields=(
            "delivery_type",
            "status",
            "stock_reserved",
        )
    )
    return order
