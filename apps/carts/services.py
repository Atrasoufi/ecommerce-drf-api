from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.carts.models import Cart, CartItem
from apps.catalog.models import ProductVariant


def get_cart(*, user):
    """Return the user's cart, if any, with related items loaded for serialization."""
    return (
        Cart.objects.filter(user=user)
        .prefetch_related("items__product", "items__variant")
        .first()
    )


def _validate_item(*, product, variant, quantity, existing_quantity=0):
    if not product.is_active:
        raise ValidationError({"product": "This product is not available."})
    if not variant.is_active:
        raise ValidationError({"variant": "This variant is not available."})
    if variant.product_id != product.pk:
        raise ValidationError(
            {"variant": "This variant does not belong to the selected product."}
        )
    if existing_quantity + quantity > variant.stock:
        raise ValidationError(
            {
                "quantity": (
                    f"Only {variant.stock} units are available. "
                    f"{existing_quantity} units are already in the cart."
                )
            }
        )


@transaction.atomic
def add_item(*, user, product, variant, quantity):
    """Add a product/variant to the user's cart or merge into an existing row."""
    locked_variant = ProductVariant.objects.select_for_update().get(pk=variant.pk)

    cart, _ = Cart.objects.get_or_create(user=user)
    item = (
        CartItem.objects.select_for_update()
        .filter(cart=cart, product=product, variant=locked_variant)
        .first()
    )

    existing_quantity = item.quantity if item else 0
    _validate_item(
        product=product,
        variant=locked_variant,
        quantity=quantity,
        existing_quantity=existing_quantity,
    )

    if item:
        item.quantity += quantity
        item.save(update_fields=["quantity"])
        return item, False

    item = CartItem.objects.create(
        cart=cart,
        product=product,
        variant=locked_variant,
        quantity=quantity,
    )
    return item, True


@transaction.atomic
def update_item(*, user, item_pk, product, variant, quantity):
    """Update one cart item after re-locking it and the destination variant."""
    item = CartItem.objects.select_for_update().get(
        pk=item_pk,
        cart__user=user,
    )
    locked_variant = ProductVariant.objects.select_for_update().get(pk=variant.pk)

    _validate_item(
        product=product,
        variant=locked_variant,
        quantity=quantity,
    )

    duplicate = (
        CartItem.objects.filter(
            cart=item.cart,
            product=product,
            variant=locked_variant,
        )
        .exclude(pk=item.pk)
        .exists()
    )
    if duplicate:
        raise ValidationError(
            {"variant": "This product/variant is already in the cart."}
        )

    item.product = product
    item.variant = locked_variant
    item.quantity = quantity
    item.save()
    return item


@transaction.atomic
def remove_item(*, user, item_pk):
    """Delete a cart item owned by ``user``."""
    item = CartItem.objects.select_for_update().get(pk=item_pk, cart__user=user)
    item.delete()
