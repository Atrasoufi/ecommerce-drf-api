from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.catalog.models import Product_Variants
from apps.orders.api.serializers.serializers import (
    OrderDetailSerializer,
    OrderListSerializer,
)
from apps.orders.models import Order


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
