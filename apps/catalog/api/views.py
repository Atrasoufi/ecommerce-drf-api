from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.viewsets import ModelViewSet

from apps.catalog.api.serializers import (
    BrandSerializer,
    CategorySerializer,
    FavoriteSerializer,
    ProductReadSerializer,
    ProductWriteSerializer,
    ReviewReadSerializer,
    ReviewWriteSerializer,
)
from apps.catalog.filters import ProductFilter
from apps.catalog.services import (
    get_brand_queryset,
    get_category_queryset,
    get_favorite_queryset,
    get_product_queryset,
    get_review_queryset,
    get_review_write_queryset,
)
from apps.core.permissions import IsOwnerOrStaffOrReadOnly, IsStaffOrReadOnly


class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return get_category_queryset()


class BrandViewSet(ModelViewSet):
    serializer_class = BrandSerializer
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        return get_brand_queryset()


class ProductViewSet(ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return get_product_queryset(
            include_inactive=self.request.user.is_staff
        )

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return ProductReadSerializer
        return ProductWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrStaffOrReadOnly]

    def get_queryset(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return get_review_write_queryset(user=self.request.user)
        return get_review_queryset(user=self.request.user)

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return ReviewReadSerializer
        return ReviewWriteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return get_favorite_queryset(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
