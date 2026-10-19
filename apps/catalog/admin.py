from django.contrib import admin
from .models import (
    Discount,
    Discount_Type,
    Products,
    Product_Images,
    Product_Variants,
    Category,
    Brands,
    Reviews,
    Favorite
)


admin.site.register(Discount)
admin.site.register(Discount_Type)
admin.site.register(Products)
admin.site.register(Product_Images)
admin.site.register(Product_Variants)
admin.site.register(Brands)
admin.site.register(Category)
admin.site.register(Reviews)
admin.site.register(Favorite)
