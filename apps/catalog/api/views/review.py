from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from apps.catalog.models import Review
from apps.catalog.api.serializers.review import ReviewSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Review.objects.filter(is_approved=True)

    def get_queryset(self):
        # اگر کاربر ادمین بود، همه نظرات (حتی تایید نشده) رو ببینه
        if self.request.user.is_staff:
            return Review.objects.all()
        # کاربران عادی فقط نظرات تایید شده رو می‌بینن
        return Review.objects.filter(is_approved=True)

    def perform_create(self, serializer):
        # وقتی کاربر نظر می‌ده، خودش به عنوان نویسنده ثبت میشه
        serializer.save(user=self.request.user)