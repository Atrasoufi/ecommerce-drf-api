from rest_framework import serializers

from apps.catalog.models import Product, ProductVariant
from apps.carts.models import Cart, CartItem


class CartItemReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "variant", "quantity"]
        read_only_fields = fields


class CartItemWriteSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = CartItem
        fields = ["product", "variant", "quantity"]


class CartReadSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "created_at", "updated_at"]
        read_only_fields = fields
