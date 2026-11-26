from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["parent"], name="category_parent_idx"),
            models.Index(fields=["is_active"], name="category_active_idx"),
        ]

    def __str__(self):
        return self.name


class DiscountType(models.Model):
    name = models.CharField(max_length=100)
    min_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "discount_types"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"], name="discount_type_active_idx"),
        ]

    def __str__(self):
        return self.name


class Discount(models.Model):
    discount = models.CharField(max_length=50)
    value = models.PositiveIntegerField(default=0)
    type = models.ForeignKey(
        DiscountType,
        on_delete=models.CASCADE,
        related_name="discounts",
    )
    max_use_all = models.PositiveIntegerField(default=0)
    max_use_user = models.PositiveIntegerField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    finish_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "discounts"
        ordering = ["discount"]
        indexes = [
            models.Index(fields=["is_active"], name="discount_active_idx"),
        ]

    def __str__(self):
        return self.discount


class Brand(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True)
    logo = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "brands"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active"], name="brand_active_idx"),
            models.Index(fields=["slug"], name="brand_slug_idx"),
        ]

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField(
        Category,
        related_name="products",
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "products"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["brand"], name="product_brand_idx"),
            models.Index(fields=["is_active"], name="product_active_idx"),
            models.Index(fields=["created_at"], name="product_created_idx"),
        ]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/", default="products/default.jpg")
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "product_images"
        ordering = ["-is_primary", "id"]
        indexes = [
            models.Index(fields=["product"], name="product_image_product_idx"),
            models.Index(fields=["is_primary"], name="product_image_primary_idx"),
        ]

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )
    sku = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=50, blank=True)
    warranty = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "product_variants"
        ordering = ["sku"]
        indexes = [
            models.Index(fields=["product"], name="product_variant_product_idx"),
            models.Index(fields=["is_active"], name="product_variant_active_idx"),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.sku}"


class Review(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5,
    )
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = "reviews"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product"], name="review_product_idx"),
            models.Index(fields=["user"], name="review_user_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product} - {self.rating}"


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="favorites",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "favorites"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product"], name="favorite_product_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_favorite",
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.product.name}"
