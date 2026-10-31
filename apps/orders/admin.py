from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem, Payment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "payment_status",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("id", "user__username", "user__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "product",
        "variant",
        "quantity",
        "unit_price",
        "discount",
        "total_price",
    )
    list_filter = ("product",)
    search_fields = ("product_name", "order__id")
    list_select_related = ("order", "product", "variant")


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "method",
        "status",
        "amount",
        "transaction_id",
        "paid_at",
        "created_at",
    )
    list_filter = ("method", "status", "created_at")
    search_fields = ("transaction_id", "order__id")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
