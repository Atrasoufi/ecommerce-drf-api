from django.contrib import admin


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("id", "cart", "product", "variant", "quantity")
    list_filter = ("variant",)
    search_fields = ("product__name","product__slug", "variant__sku","cart__user__email",   )
