from django.db import models



#پیشنهادی ----------
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from apps.catalog.models import Products, Product_Variants

class Order(models.Model):
    # طبق ERD: user_id, address_id
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    
    # فرض بر این است که یک مدل Address در اپلیکیشن accounts دارید. 
    # اگر اسمش چیز دیگری است، آن را تغییر دهید.
    address = models.ForeignKey("accounts.Address", on_delete=models.SET_NULL, null=True, blank=True)
    
    # طبق ERD: status, payment_status
    status = models.CharField(max_length=30, default="pending")
    payment_status = models.CharField(max_length=30, default="unpaid")
    
    # طبق ERD: مبالغ
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def str(self):
        return f"Order {self.id} by {self.user}"


class OrderItem(models.Model):
    # طبق ERD: order_id, product_id, variant_id
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant = models.ForeignKey(Product_Variants, on_delete=models.SET_NULL, null=True, blank=True)
    
    # طبق ERD: product_name, unit_price, discount, quantity, total_price
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def str(self):
        return f"{self.product_name} (x{self.quantity})"




# Create your models here.
