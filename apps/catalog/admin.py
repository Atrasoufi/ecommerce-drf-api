from django.contrib import admin
from .models import (
    Discount,
    Discount_Type,
    Products,
    Product_Images,
    Product_Variants
)
admin.site.register(Discount)
admin.site.register(Discount_Type)
admin.site.register(Products)
admin.site.register(Product_Images)
admin.site.register(Product_Variants)


# Register your models here.
