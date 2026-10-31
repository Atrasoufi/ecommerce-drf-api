from rest_framework import serializers

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
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
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
