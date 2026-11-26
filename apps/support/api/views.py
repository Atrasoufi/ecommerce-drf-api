from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser

from apps.core.permissions import IsStaffOrReadOnly
from apps.support.api.serializers import (
    ContactMessageSerializer,
    FAQSerializer,
)
from apps.support.models import ContactMessage, FAQ


class FAQViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = FAQ.objects.all().order_by("display_order", "created_at")
        user = self.request.user
        if not (user.is_authenticated and user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset


class ContactMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ContactMessageSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return ContactMessage.objects.select_related("user").all()

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user if user.is_authenticated else None)
