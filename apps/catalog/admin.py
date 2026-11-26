from django.contrib import admin

from .models import (
    Brand,
    Category,
    Discount,
    DiscountType,
    Favorite,
    Product,
    ProductImage,
    ProductVariant,
    Review,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "parent", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "brand", "is_active", "created_at")
    list_filter = ("is_active", "brand", "categories")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    list_select_related = ("brand",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "sku", "color", "price", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("sku", "product__name")
    list_select_related = ("product",)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "is_primary")
    list_filter = ("is_primary",)
    list_select_related = ("product",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "is_approved")
    list_filter = ("is_approved", "rating")
    search_fields = ("product__name", "user__email")
    list_select_related = ("product", "user")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "created_at")
    search_fields = ("user__email", "product__name")
    list_select_related = ("user", "product")


admin.site.register(Discount)
admin.site.register(DiscountType)
