from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.orders.api.serializers import (
    CreateOrderSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.orders.services import cancel_order, create_order_from_cart, get_order_queryset


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        queryset = get_order_queryset(user=self.request.user)
        order_status = self.request.query_params.get("status")
        if order_status:
            queryset = queryset.filter(status=order_status)
        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CreateOrderSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        return OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = create_order_from_cart(
            user=request.user,
            address=serializer.validated_data["address"],
        )
        return Response(
            {
                "message": "Order created successfully.",
                "order_id": order.id,
                "subtotal": order.subtotal,
                "discount": order.discount,
                "shipping_cost": order.shipping_cost,
                "total_price": order.total_price,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        order = cancel_order(user=request.user, order_pk=pk)
        return Response(
            {
                "detail": "Order cancelled successfully.",
                "order_id": order.pk,
                "status": order.status,
                "payment_status": order.payment_status,
            },
            status=status.HTTP_200_OK,
        )
