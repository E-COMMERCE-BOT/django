from django.contrib import admin

from .models import DeliveryType, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("total",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "status",
        "delivery_type",
        "total",
        "created_at",
    )
    list_filter = ("status", "delivery_type")
    search_fields = ("number", "user__tg_id", "user__name")
    inlines = (OrderItemInline,)


@admin.register(DeliveryType)
class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "price")
