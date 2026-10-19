from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from ...models import Cart, CartItem
from ....catalog.models import Product_Variants
from ..serializers.serializers import (
    CartReadSerializer,
    CartItemReadSerializer,
    CartItemWriteSerializer,
)


# نمایش سبد خرید کاربر فعلی
class CartView(RetrieveAPIView):
    serializer_class = CartReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(
            user=self.request.user
        )
        return cart


# مدیریت آیتم‌های سبد خرید
class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        ).select_related(
            "cart",
            "product",
            "variant",
        )

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return CartItemReadSerializer

        return CartItemWriteSerializer

    # افزودن آیتم به سبد خرید
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        variant = serializer.validated_data["variant"]
        quantity = serializer.validated_data["quantity"]

        with transaction.atomic():
            # قفل تنوع برای جلوگیری از تداخل درخواست‌های هم‌زمان
            locked_variant = (
                Product_Variants.objects
                .select_for_update()
                .get(pk=variant.pk)
            )

            # بررسی وضعیت فعلی محصول و تنوع
            if not product.is_active:
                raise ValidationError({
                    "product": "این محصول غیرفعال است."
                })

            if not locked_variant.is_active:
                raise ValidationError({
                    "variant": "این تنوع غیرفعال است."
                })

            if locked_variant.product_id != product.id:
                raise ValidationError({
                    "variant": "این تنوع متعلق به این محصول نیست."
                })

            # ساخت خودکار سبد خرید
            cart, _ = Cart.objects.get_or_create(
                user=request.user
            )

            # پیدا کردن آیتم موجود برای همین محصول و تنوع
            item = (
                CartItem.objects
                .select_for_update()
                .filter(
                    cart=cart,
                    product=product,
                    variant=locked_variant,
                )
                .first()
            )

            if item:
                # تعداد نهایی شامل تعداد قبلی و جدید است
                new_quantity = item.quantity + quantity

                if new_quantity > locked_variant.stock:
                    raise ValidationError({
                        "quantity": (
                            f"موجودی این تنوع "
                            f"{locked_variant.stock} عدد است. "
                            f"تعداد فعلی سبد: {item.quantity} عدد."
                        )
                    })

                item.quantity = new_quantity
                item.save(update_fields=["quantity"])

                response_status = status.HTTP_200_OK

            else:
                # بررسی موجودی برای آیتم جدید
                if quantity > locked_variant.stock:
                    raise ValidationError({
                        "quantity": (
                            f"موجودی این تنوع "
                            f"{locked_variant.stock} عدد است."
                        )
                    })

                item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=locked_variant,
                    quantity=quantity,
                )

                response_status = status.HTTP_201_CREATED

        output_serializer = CartItemReadSerializer(
            item,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=response_status,
        )

    # ویرایش کامل یا جزئی آیتم
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)

        # ابتدا مطمئن می‌شویم آیتم متعلق به کاربر فعلی است
        current_item = self.get_object()

        # اعتبارسنجی اولیه برای مشخص شدن تنوع مقصد
        initial_serializer = self.get_serializer(
            current_item,
            data=request.data,
            partial=partial,
        )
        initial_serializer.is_valid(raise_exception=True)

        variant = initial_serializer.validated_data.get(
            "variant",
            current_item.variant,
        )

        with transaction.atomic():
            # قفل تنوع مقصد
            locked_variant = (
                Product_Variants.objects
                .select_for_update()
                .get(pk=variant.pk)
            )

            # دریافت مجدد آیتم با محدودیت مالکیت
            item = (
                CartItem.objects
                .select_for_update()
                .get(
                    pk=current_item.pk,
                    cart__user=request.user,
                )
            )

            # اعتبارسنجی مجدد با وضعیت تازه
            serializer = self.get_serializer(
                item,
                data=request.data,
                partial=partial,
            )
            serializer.is_valid(raise_exception=True)

            product = serializer.validated_data.get(
                "product",
                item.product,
            )

            quantity = serializer.validated_data.get(
                "quantity",
                item.quantity,
            )

            if not product.is_active:
                raise ValidationError({
                    "product": "این محصول غیرفعال است."
                })

            if not locked_variant.is_active:
                raise ValidationError({
                    "variant": "این تنوع غیرفعال است."
                })

            if locked_variant.product_id != product.id:
                raise ValidationError({
                    "variant": "این تنوع متعلق به این محصول نیست."
                })

            # بررسی موجودی تنوع مقصد
            if quantity > locked_variant.stock:
                raise ValidationError({
                    "quantity": (
                        f"موجودی این تنوع "
                        f"{locked_variant.stock} عدد است."
                    )
                })

            # جلوگیری از ایجاد آیتم تکراری هنگام تغییر تنوع
            duplicate = CartItem.objects.filter(
                cart=item.cart,
                product=product,
                variant=locked_variant,
            ).exclude(pk=item.pk).exists()

            if duplicate:
                raise ValidationError({
                    "variant": (
                        "این محصول با همین تنوع از قبل "
                        "در سبد خرید وجود دارد. ابتدا آیتم موجود "
                        "را ویرایش یا حذف کنید."
                    )
                })

            serializer.save(variant=locked_variant)

        output_serializer = CartItemReadSerializer(
            item,
            context=self.get_serializer_context(),
        )

        return Response(output_serializer.data)

    # حذف آیتم
    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        self.perform_destroy(item)

        return Response(status=status.HTTP_204_NO_CONTENT)