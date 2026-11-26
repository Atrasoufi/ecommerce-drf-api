from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.carts.api.serializers import (
    CartItemReadSerializer,
    CartItemWriteSerializer,
    CartReadSerializer,
)
from apps.carts.models import CartItem
from apps.carts.services import add_item, get_cart, remove_item, update_item


class CartView(APIView):
    serializer_class = CartReadSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart = get_cart(user=request.user)
        if cart is None:
            return Response(
                {
                    "id": None,
                    "items": [],
                    "created_at": None,
                    "updated_at": None,
                }
            )
        return Response(CartReadSerializer(cart).data)


class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user).select_related(
            "cart", "product", "variant"
        )

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return CartItemReadSerializer
        return CartItemWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item, created = add_item(
            user=request.user,
            product=serializer.validated_data["product"],
            variant=serializer.validated_data["variant"],
            quantity=serializer.validated_data["quantity"],
        )
        item.refresh_from_db()
        return Response(
            CartItemReadSerializer(
                item, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        current_item = self.get_object()

        serializer = self.get_serializer(
            current_item, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        item = update_item(
            user=request.user,
            item_pk=current_item.pk,
            product=serializer.validated_data.get(
                "product", current_item.product
            ),
            variant=serializer.validated_data.get(
                "variant", current_item.variant
            ),
            quantity=serializer.validated_data.get(
                "quantity", current_item.quantity
            ),
        )
        return Response(
            CartItemReadSerializer(
                item, context=self.get_serializer_context()
            ).data
        )

    def destroy(self, request, *args, **kwargs):
        item = self.get_object()
        remove_item(user=request.user, item_pk=item.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)
