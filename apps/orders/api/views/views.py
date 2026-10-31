from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.orders.models import Order
from apps.catalog.models import Product_Variants


class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():

            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk,
                user=request.user,
            )

            # Check order status
            if order.status not in [
                Order.Status.PENDING,
                Order.Status.PROCESSING,
            ]:
                return Response(
                    {"detail": "This order cannot be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Only unpaid orders can be cancelled
            if order.payment_status != Order.PaymentStatus.PENDING:
                return Response(
                    {"detail": "Paid orders cannot be cancelled."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Restore product variant stock
            for item in order.items.select_related("variant"):
                if item.variant_id is None:
                    continue

                variant = Product_Variants.objects.select_for_update().get(
                    pk=item.variant_id
                )

                variant.stock += item.quantity
                variant.save(update_fields=["stock"])

            # Update order status
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