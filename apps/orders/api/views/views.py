
from rest_framework import viewsets, permissions
from apps.orders.models import Order
from apps.orders.api.serializers.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderListSerializer
