from rest_framework import serializers
from apps.accounts.models import Address
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
    # آدرس ارسال سفارش از سمت کاربر دریافت می‌شود
    address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all()
    )

    def validate_address(self, address):
        # فقط اجازه استفاده از آدرس متعلق به کاربر واردشده را می‌دهیم
        user = self.context["request"].user

        if address.user_id != user.id:
            raise serializers.ValidationError(
                "You can only use your own addresses."
            )

        return address