from django.db import models
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    # parent = models.ForeignKey(
    #     "self",
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="children",
    # )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Discount_Type(models.Model):
     name = models.CharField(max_length=100)
     min_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
     is_active = models.BooleanField(default=True)

     def __str__(self):
        return self.name

class Discount(models.Model):
    discount = models.CharField(max_length=50)
    value = models.PositiveIntegerField(default=0)
    type = models.ForeignKey(Discount_Type,on_delete=models.CASCADE)
    max_use_all = models.PositiveIntegerField(default=0)
    max_use_user = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField(null=True,blank=True)
    finish_time = models.DateTimeField(null=True,blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
            return self.discount

class Products(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(Category,)
    brand = models.ForeignKey("Brands", on_delete=models.SET_NULL,null=True)
    discount = models.ForeignKey(Discount,on_delete=models.DO_NOTHING)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

class Product_Images(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    image = models.ImageField(upload_to="products/",default="products/default.jpg")
    is_primary = models.BooleanField(default=True)

    def __str__(self):
            return self.product.name

class Product_Variants(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    sku = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    warranty = models.CharField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.product.name} - {self.sku} - {self.color} - {self.warranty}"


# Create your models here.
class Review(models.Model):
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    # فرض بر این است که مدل کاربری پروژه شما در اپلیکیشن accounts تعریف شده است.
    # اگر اسم مدل کاربری شما چیز دیگری است (مثلاً User)، آن را جایگزین کنید.
    user = models.ForeignKey(
        "accounts.User", 
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)], # طبق ساختار شما، فقط حداقل را تعیین کردیم
        default=5
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        # جلوگیری از ثبت چند نظر برای یک محصول توسط یک کاربر
        unique_together = ("product", "user")

    def str(self):
        return f"{self.user} - {self.product.name} ({self.rating})"


class Favorite(models.Model):
    user = models.ForeignKey(
        "accounts.User", 
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        # جلوگیری از لایک تکراری یک محصول توسط یک کاربر
        unique_together = ("user", "product")

    def str(self):
        return f"{self.user} -> {self.product.name}"