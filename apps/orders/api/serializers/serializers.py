from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.accounts.models import Address
from apps.carts.models import Cart
from apps.catalog.models import Product_Variants
from apps.orders.models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "variant",
            "product_name",
            "unit_price",
            "discount",
            "quantity",
            "total_price",
        ]
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "method",
            "status",
            "amount",
            "transaction_id",
            "paid_at",
            "created_at",
        ]
        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "payment_status",
            "total_price",
            "created_at",
        ]
        read_only_fields = fields


class OrderDetailSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "address",
            "status",
            "payment_status",
            "subtotal",
            "discount",
            "shipping_cost",
            "total_price",
            "items",
            "payments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CreateOrderSerializer(serializers.Serializer):
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all()
    )

    def validate_address(self, address):
        # Only allow using addresses belonging to the authenticated user
        user = self.context["request"].user
        if address.user_id != user.id:
            raise serializers.ValidationError(
                "You can only use your own addresses."
            )
        return address

    @transaction.atomic
    def create(self, validated_data):
        user = self.context["request"].user
        address = validated_data["address"]

        # Retrieve the user's cart with a database lock
        try:
            cart = Cart.objects.select_for_update().get(user=user)
        except Cart.DoesNotExist:
            raise ValidationError("Your cart is empty.")

        cart_items = list(cart.items.select_related("product", "variant").all())
        if not cart_items:
            raise ValidationError("Your cart is empty.")

        for item in cart_items:
            if item.variant_id is None:
                raise ValidationError("A cart item has no variant.")

        variant_ids = sorted({item.variant_id for item in cart_items})
        
        # Retrieve and lock all variants ordered by PK to prevent deadlocks
        locked_variants = {
            variant.pk: variant
            for variant in Product_Variants.objects.select_for_update()
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
                raise ValidationError("A product is not available.")
            
            required_quantities[variant.pk] = (
                required_quantities.get(variant.pk, 0) + item.quantity
            )

        # Check stock availability
        for variant_id, quantity in required_quantities.items():
            variant = locked_variants[variant_id]
            if variant.stock < quantity:
                raise ValidationError(f"Not enough stock for {variant.product.name}.")

        discount = 0
        shipping_cost = 0
        subtotal = sum(
            locked_variants[item.variant_id].price * item.quantity
            for item in cart_items
        )
        total_price = subtotal - discount + shipping_cost

        # Create the main order
        order = Order.objects.create(
            user=user,
            address=address,
            subtotal=subtotal,
            discount=discount,
            shipping_cost=shipping_cost,
            total_price=total_price,
        )

        # Create order items with snapshot data
        for item in cart_items:
            variant = locked_variants[item.variant_id]
            unit_price = variant.price
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=variant,
                product_name=item.product.name,
                unit_price=unit_price,
                discount=0,
                quantity=item.quantity,
                total_price=unit_price * item.quantity,
            )

        # Deduct stock
        for variant_id, quantity in required_quantities.items():
            variant = locked_variants[variant_id]
            variant.stock -= quantity
            variant.save(update_fields=["stock"])

        # Create initial payment record
        Payment.objects.create(
            order=order,
            method=Payment.Method.ONLINE,
            amount=total_price,
        )

        # Clear the cart
        cart.items.all().delete()

        # Return the order object to be used in the View
        return order