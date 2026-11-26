from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    class Meta:
        db_table = "carts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cart #{self.pk} - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(
        "carts.Cart",
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        "catalog.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )

    class Meta:
        db_table = "cart_items"
        ordering = ["id"]
        indexes = [
            models.Index(fields=["cart"], name="cart_item_cart_idx"),
            models.Index(fields=["product"], name="cart_item_product_idx"),
            models.Index(fields=["variant"], name="cart_item_variant_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "product", "variant"],
                name="cartitem_cart_product_variant_uniq",
            ),
            models.UniqueConstraint(
                fields=["cart", "product"],
                condition=models.Q(variant__isnull=True),
                name="cartitem_cart_product_no_var_uniq",
            ),
        ]

    def __str__(self):
        return f"{self.product} x {self.quantity}"
