from decimal import Decimal

from django.db import models

from apps.catalog.models import Product
from apps.users.models import User


class OrderStatus(models.TextChoices):
    CART = "cart", "Cart"
    CREATED = "created", "Created"
    PROCESSING = "processing", "Processing"
    SHIPPED = "shipped", "Shipped"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"


class DeliveryType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("price",)

    def __str__(self) -> str:
        return self.name


class Order(models.Model):
    number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        null=True,
        blank=True,
    )
    user = models.ForeignKey(
        User,
        related_name="orders",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.CART,
        db_index=True,
    )
    delivery_type = models.ForeignKey(
        DeliveryType,
        related_name="orders",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )
    stock_reserved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user",),
                condition=models.Q(status=OrderStatus.CART),
                name="unique_active_cart_per_user",
            )
        ]

    @property
    def total(self) -> Decimal:
        items_total = sum(
            (item.total for item in self.items.select_related("product")),
            Decimal("0.00"),
        )
        delivery_price = (
            self.delivery_type.price
            if self.delivery_type
            else Decimal("0.00")
        )
        return items_total + delivery_price

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)
        if creating and not self.number:
            self.number = f"ORD-{self.pk:06d}"
            super().save(update_fields=("number",))

    def __str__(self) -> str:
        return self.number or f"Order {self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        related_name="order_items",
        on_delete=models.PROTECT,
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("order", "product"),
                name="unique_product_per_order",
            )
        ]

    @property
    def total(self) -> Decimal:
        return self.product.price * self.quantity

    def __str__(self) -> str:
        return f"{self.product.name} x {self.quantity}"
