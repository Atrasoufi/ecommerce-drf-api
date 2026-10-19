from rest_framework import serializers

from ...models import Cart, CartItem
from catalog.models import Products, Product_Variants


# Serializer پایه سبد خرید
class CartBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]


# Serializer مخصوص نمایش سبد خرید
class CartReadSerializer(CartBaseSerializer):
    items = serializers.SerializerMethodField()

    class Meta(CartBaseSerializer.Meta):
        fields = CartBaseSerializer.Meta.fields + ["items"]

    def get_items(self, obj):
        return CartItemReadSerializer(
            obj.items.all(),
            many=True,
            context=self.context,
        ).data


# Serializer مخصوص ایجاد و ویرایش سبد خرید
class CartWriteSerializer(CartBaseSerializer):
    class Meta(CartBaseSerializer.Meta):
        fields = []


# Serializer پایه آیتم سبد خرید
class CartItemBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "variant",
            "quantity",
        ]
        read_only_fields = ["id"]


# Serializer مخصوص نمایش آیتم سبد خرید
class CartItemReadSerializer(CartItemBaseSerializer):
    class Meta(CartItemBaseSerializer.Meta):
        fields = [
            "id",
            "product",
            "variant",
            "quantity",
        ]


# Serializer مخصوص ایجاد و ویرایش آیتم سبد خرید
class CartItemWriteSerializer(CartItemBaseSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all()
    )

    variant = serializers.PrimaryKeyRelatedField(
        queryset=Product_Variants.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta(CartItemBaseSerializer.Meta):
        fields = [
            "product",
            "variant",
            "quantity",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "تعداد محصول باید حداقل ۱ باشد."
            )

        return value

    def validate(self, attrs):
        product = attrs.get(
            "product",
            getattr(self.instance, "product", None),
        )

        variant = attrs.get(
            "variant",
            getattr(self.instance, "variant", None),
        )

        if (
            variant is not None
            and product is not None
            and variant.product_id != product.id
        ):
            raise serializers.ValidationError({
                "variant": "این تنوع متعلق به محصول انتخاب‌شده نیست."
            })

        return attrs