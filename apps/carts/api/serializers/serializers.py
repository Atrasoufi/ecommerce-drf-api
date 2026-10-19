from rest_framework import serializers

from ...models import Cart, CartItem
from ....catalog.models import Products, Product_Variants


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
    class Meta:
        model = Cart
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
        required=True,
        allow_null=False,
    )

    class Meta(CartItemBaseSerializer.Meta):
        fields = [
            "product",
            "variant",
            "quantity",
        ]

    # بررسی تعداد درخواستی
    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "تعداد محصول باید حداقل ۱ باشد."
            )

        return value

    # اعتبارسنجی محصول، تنوع و موجودی
    def validate(self, attrs):
        product = attrs.get(
            "product",
            getattr(self.instance, "product", None),
        )

        variant = attrs.get(
            "variant",
            getattr(self.instance, "variant", None),
        )

        quantity = attrs.get(
            "quantity",
            getattr(self.instance, "quantity", 1),
        )

        # انتخاب تنوع الزامی است
        if variant is None:
            raise serializers.ValidationError({
                "variant": "انتخاب تنوع محصول الزامی است."
            })

        # بررسی تعلق تنوع به محصول
        if product is not None and variant.product_id != product.id:
            raise serializers.ValidationError({
                "variant": (
                    "این تنوع متعلق به محصول انتخاب‌شده نیست."
                )
            })

        # بررسی فعال بودن محصول
        if product is not None and not product.is_active:
            raise serializers.ValidationError({
                "product": "این محصول غیرفعال است."
            })

        # بررسی فعال بودن تنوع
        if not variant.is_active:
            raise serializers.ValidationError({
                "variant": "این تنوع غیرفعال است."
            })

        # بررسی موجودی انبار
        if quantity > variant.stock:
            raise serializers.ValidationError({
                "quantity": (
                    f"موجودی این تنوع {variant.stock} عدد است."
                )
            })

        return attrs