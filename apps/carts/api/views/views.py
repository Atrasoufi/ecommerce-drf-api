
from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Cart, CartItem
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            cart, _ = Cart.objects.get_or_create(
                user=request.user
            )

            product = serializer.validated_data["product"]
            variant = serializer.validated_data.get("variant")
            quantity = serializer.validated_data["quantity"]

            item = CartItem.objects.filter(
                cart=cart,
                product=product,
                variant=variant,
            ).first()

            if item:
                item.quantity += quantity
                item.save(update_fields=["quantity"])
                response_status = status.HTTP_200_OK
            else:
                item = serializer.save(cart=cart)
                response_status = status.HTTP_201_CREATED

        output_serializer = CartItemReadSerializer(
            item,
            context=self.get_serializer_context(),
        )

        return Response(
            output_serializer.data,
            status=response_status,
        )
