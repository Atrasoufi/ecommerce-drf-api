from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
        db_index=False,
    )

    address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=False,
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        indexes = [
            models.Index(fields=["user"], name="order_user_idx"),
            models.Index(fields=["address"], name="order_address_idx"),
            models.Index(fields=["status"], name="order_status_idx"),
            models.Index(
                fields=["payment_status"],
                name="order_payment_status_idx",
            ),
            models.Index(fields=["created_at"], name="order_created_idx"),
        ]

    def __str__(self):
        return f"Order #{self.pk}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="items",
        db_index=False,
    )

    product = models.ForeignKey(
        "catalog.Products",
        on_delete=models.PROTECT,
        related_name="order_items",
        db_index=False,
    )

    variant = models.ForeignKey(
        "catalog.Product_Variants",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
        db_index=False,
    )

    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )

    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "order_items"
        indexes = [
            models.Index(fields=["order"], name="orderitem_order_idx"),
            models.Index(fields=["product"], name="orderitem_product_idx"),
            models.Index(fields=["variant"], name="orderitem_variant_idx"),
        ]

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"


class Payment(models.Model):

    class Method(models.TextChoices):
        ONLINE = "online", "Online"
        CARD_TO_CARD = "card_to_card", "Card to card"
        CASH = "cash", "Cash"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
        db_index=False,
    )

    method = models.CharField(max_length=30, choices=Method.choices)

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    transaction_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )

    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        indexes = [
            models.Index(fields=["order"], name="payment_order_idx"),
            models.Index(fields=["status"], name="payment_status_idx"),
            models.Index(
                fields=["transaction_id"],
                name="payment_transaction_idx",
            ),
        ]

    def __str__(self):
        return f"Payment #{self.pk} - {self.status}"
