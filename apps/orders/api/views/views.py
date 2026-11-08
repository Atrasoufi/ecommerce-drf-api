from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.models import Cart
from apps.catalog.models import Product_Variants
from apps.orders.api.serializers.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.orders.models import Order, OrderItem, Payment

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        order_status = self.request.query_params.get("status")

        if order_status:
            queryset = queryset.filter(status=order_status)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderListSerializer


class CancelOrderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk,
                user=request.user,
            )

            if order.status not in (
                Order.Status.PENDING,
                Order.Status.PROCESSING,
            ):
                return Response(
                    {"detail": "This order cannot be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            unpaid_statuses = {
                Order.PaymentStatus.PENDING,
                Order.PaymentStatus.UNPAID,
            }
            if order.payment_status not in unpaid_statuses:
                return Response(
                    {"detail": "Paid orders cannot be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Lock order items, then lock each variant before restoring stock.
            items = order.items.select_for_update().order_by("pk")
            for item in items:
                if item.variant_id is None:
                    continue

                variant = Product_Variants.objects.select_for_update().get(
                    pk=item.variant_id
                )
                variant.stock += item.quantity
                variant.save(update_fields=["stock"])

            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])

        return Response(
            {
                "detail": "Order cancelled successfully.",
                "order_id": order.pk,
                "status": order.status,
                "payment_status": order.payment_status,
            },
            status=status.HTTP_200_OK,
        )


class CreateOrderAPIView(APIView):
    # فقط کاربران احراز هویت‌شده می‌توانند سفارش ثبت کنند
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        # اعتبارسنجی آدرس ارسال
        serializer = CreateOrderSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        address = serializer.validated_data["address"]

        # دریافت سبد خرید کاربر با قفل دیتابیس
        try:
            cart = Cart.objects.select_for_update().get(
                user=request.user
            )
        except Cart.DoesNotExist:
            raise ValidationError("Your cart is empty.")

        # دریافت آیتم‌های سبد خرید
        cart_items = list(
            cart.items.select_related(
                "product",
                "variant",
            ).all()
        )

        if not cart_items:
            raise ValidationError("Your cart is empty.")

        # بررسی اینکه تمام آیتم‌ها دارای تنوع محصول باشند
        for item in cart_items:
            if item.variant_id is None:
                raise ValidationError(
                    "A cart item has no variant."
                )

        # شناسه تنوع‌های موجود در سبد خرید
        variant_ids = sorted({
            item.variant_id for item in cart_items
        })

        # دریافت و قفل‌کردن تمام تنوع‌ها به ترتیب شناسه
        locked_variants = {
            variant.pk: variant
            for variant in Product_Variants.objects.select_for_update()
            .filter(pk__in=variant_ids)
            .order_by("pk")
        }

        # جمع تعداد موردنیاز هر تنوع محصول
        required_quantities = {}

        for item in cart_items:
            variant = locked_variants.get(item.variant_id)

            # بررسی وجود تنوع محصول
            if variant is None:
                raise ValidationError(
                    "A product variant does not exist."
                )

            # بررسی ارتباط تنوع با محصول
            if variant.product_id != item.product_id:
                raise ValidationError(
                    "Product and variant do not match."
                )

            # بررسی فعال بودن محصول و تنوع
            if not item.product.is_active or not variant.is_active:
                raise ValidationError(
                    "A product is not available."
                )

            # جمع تعداد موردنیاز برای هر تنوع
            required_quantities[variant.pk] = (
                required_quantities.get(variant.pk, 0)
                + item.quantity
            )

        # بررسی موجودی تمام تنوع‌ها قبل از ایجاد سفارش
        for variant_id, quantity in required_quantities.items():
            variant = locked_variants[variant_id]

            if variant.stock < quantity:
                raise ValidationError(
                    f"Not enough stock for {variant.product.name}."
                )

        # فعلاً تخفیف و هزینه ارسال صفر هستند
        # چون فرمول تخفیف و سیاست هزینه ارسال مشخص نشده است
        discount = 0
        shipping_cost = 0

        # محاسبه مبلغ کالاهای سبد خرید
        subtotal = sum(
            locked_variants[item.variant_id].price * item.quantity
            for item in cart_items
        )

        # محاسبه مبلغ نهایی سفارش
        total_price = subtotal - discount + shipping_cost

        # ایجاد سفارش اصلی
        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=subtotal,
            discount=discount,
            shipping_cost=shipping_cost,
            total_price=total_price,
        )

        # ایجاد آیتم‌های سفارش با اطلاعات محصول در زمان خرید
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

        # کاهش موجودی پس از بررسی تمام آیتم‌ها
        for variant_id, quantity in required_quantities.items():
            variant = locked_variants[variant_id]
            variant.stock -= quantity
            variant.save(update_fields=["stock"])

        # ایجاد پرداخت اولیه با وضعیت Pending
        Payment.objects.create(
            order=order,
            method=Payment.Method.ONLINE,
            amount=total_price,
        )

        # خالی کردن سبد خرید پس از موفقیت عملیات
        cart.items.all().delete()

        return Response(
            {
                "message": "Order created successfully.",
                "order_id": order.id,
                "subtotal": subtotal,
                "discount": discount,
                "shipping_cost": shipping_cost,
                "total_price": total_price,
            },
            status=status.HTTP_201_CREATED,
        )
