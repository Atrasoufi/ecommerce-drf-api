from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.carts.models import Cart
from apps.catalog.models import ProductVariant
from apps.orders.models import Order, OrderItem, Payment


def get_order_queryset(*, user):
    """Return the user's orders with all nested serializers preloaded."""
    return (
        Order.objects.filter(user=user)
        .select_related("user", "address")
        .prefetch_related("items__product", "items__variant", "payments")
        .order_by("-created_at")
    )


@transaction.atomic
def create_order_from_cart(*, user, address):
    """Create an order from the user's cart and restore consistent stock."""
    cart = Cart.objects.select_for_update().filter(user=user).first()
    cart_items = list(cart.items.select_related("product", "variant")) if cart else []

    if not cart_items:
        raise ValidationError("Your cart is empty.")

    if any(item.variant_id is None for item in cart_items):
        raise ValidationError("Every cart item must have a product variant.")

    variant_ids = sorted({item.variant_id for item in cart_items})
    locked_variants = {
        variant.pk: variant
        for variant in ProductVariant.objects.select_for_update()
        .filter(pk__in=variant_ids)
        .order_by("pk")
    }

    required_quantities = {}
    for item in cart_items:
        variant = locked_variants.get(item.variant_id)
        if variant is None:
            raise ValidationError("A product variant does not exist.")
        if variant.product_id != item.product_id:
            raise ValidationError("Product and variant do not match.")
        if not item.product.is_active or not variant.is_active:
            raise ValidationError("A product in the cart is not available.")

        required_quantities[variant.pk] = (
            required_quantities.get(variant.pk, 0) + item.quantity
        )

    for variant_id, quantity in required_quantities.items():
        variant = locked_variants[variant_id]
        if variant.stock < quantity:
            raise ValidationError(
                f"Not enough stock for {variant.product.name}."
            )

    discount = 0
    shipping_cost = 0
    subtotal = sum(
        locked_variants[item.variant_id].price * item.quantity
        for item in cart_items
    )
    total_price = subtotal - discount + shipping_cost

    order = Order.objects.create(
        user=user,
        address=address,
        subtotal=subtotal,
        discount=discount,
        shipping_cost=shipping_cost,
        total_price=total_price,
    )

    OrderItem.objects.bulk_create(
        [
            OrderItem(
                order=order,
                product=item.product,
                variant=locked_variants[item.variant_id],
                product_name=item.product.name,
                unit_price=locked_variants[item.variant_id].price,
                discount=0,
                quantity=item.quantity,
                total_price=locked_variants[item.variant_id].price
                * item.quantity,
            )
            for item in cart_items
        ]
    )

    for variant_id, quantity in required_quantities.items():
        variant = locked_variants[variant_id]
        variant.stock -= quantity
        variant.save(update_fields=["stock"])

    Payment.objects.create(
        order=order,
        method=Payment.Method.ONLINE,
        amount=total_price,
    )

    cart.items.all().delete()
    return order


@transaction.atomic
def cancel_order(*, user, order_pk):
    """Cancel an unpaid pending/processing order and restore its stock."""
    order = get_object_or_404(
        Order.objects.select_for_update(),
        pk=order_pk,
        user=user,
    )

    if order.status not in (Order.Status.PENDING, Order.Status.PROCESSING):
        raise ValidationError("This order cannot be cancelled.")

    unpaid_statuses = {Order.PaymentStatus.PENDING, Order.PaymentStatus.UNPAID}
    if order.payment_status not in unpaid_statuses:
        raise ValidationError("Paid orders cannot be cancelled.")

    items = list(order.items.select_for_update().order_by("pk"))
    variant_ids = sorted({item.variant_id for item in items if item.variant_id})
    locked_variants = {
        variant.pk: variant
        for variant in ProductVariant.objects.select_for_update()
        .filter(pk__in=variant_ids)
        .order_by("pk")
    }

    for item in items:
        variant = locked_variants.get(item.variant_id)
        if variant:
            variant.stock += item.quantity
            variant.save(update_fields=["stock"])

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    return order
