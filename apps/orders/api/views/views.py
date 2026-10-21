from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions
from apps.orders.models import Order
from apps.orders.api.serializers import OrderListSerializer, OrderDetailSerializer

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # امنیت: هر کاربری فقط سفارشات خودش را می‌بیند
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        # اگر درخواست برای دیدن یک سفارش خاص بود، سریالایزر جزئیات را بده
        if self.action == 'retrieve':
            return OrderDetailSerializer
        # وگرنه (برای لیست) سریالایزر لیست را بده
        return OrderListSerializer