from rest_framework.viewsets import ModelViewSet

from ...models import FAQ
from ..serializers.serializers import FAQSerializer
from .permissions import IsStaffOrReadOnly


class FAQViewSet(ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        queryset = FAQ.objects.all().order_by(
            "display_order",
            "created_at",
        )

        user = self.request.user

        if not (user.is_authenticated and user.is_staff):
            queryset = queryset.filter(is_active=True)

        return queryset