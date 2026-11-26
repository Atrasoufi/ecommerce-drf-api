from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at", "updated_at")
    search_fields = ("user__email",)
    list_select_related = ("user",)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "variant", "quantity")
    list_filter = ("variant",)
    search_fields = (
        "product__name",
        "product__slug",
        "variant__sku",
        "cart__user__email",
    )
    list_select_related = ("cart", "product", "variant")
