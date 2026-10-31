
from rest_framework import serializers
from apps.orders.models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product_name",
            "unit_price",
            "discount",
            "quantity",
            "total_price",
        ]


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "status",
            "total_price",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

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
            "created_at",
            "updated_at",
        ]
