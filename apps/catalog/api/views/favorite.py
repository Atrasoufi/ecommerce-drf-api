from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.catalog.models import Favorite
from apps.catalog.api.serializers.favorite import FavoriteSerializer

class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # هر کاربر فقط لیست علاقه‌مندی‌های خودش رو می‌بینه
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # کاربر رو خودکار ثبت می‌کنه
        serializer.save(user=self.request.user)