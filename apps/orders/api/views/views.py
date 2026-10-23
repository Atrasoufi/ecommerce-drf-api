from django.shortcuts import render

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ...models import Order
from ....catalog.models import Products


class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=pk,
                user=request.user,
            )

            if order.status not in ["pending", "processing"]:
                return Response(
                    {
                        "detail": "This order cannot be cancelled."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for item in order.items.all():
                product = Products.objects.select_for_update().get(
                    pk=item.product_id
                )

                product.stock += item.quantity
                product.save(update_fields=["stock"])

            order.status = "cancelled"

            if order.payment_status == "pending":
                order.payment_status = "cancelled"

            order.save(
                update_fields=["status", "payment_status"]
            )

        return Response(
            {
                "detail": "Order cancelled successfully.",
                "order_id": order.pk,
                "status": order.status,
                "payment_status": order.payment_status,
            },
            status=status.HTTP_200_OK,
        )
