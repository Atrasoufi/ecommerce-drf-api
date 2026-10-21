from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from ...models import Category, Brands, Products, Product_Images, Product_Variants
from ..serializers.seralizers import (
    CategoryReadSerializer,
    CategoryWriteSerializer,
    BrandsReadSerializer,
    BrandsWriteSerializer,
    
    ProductsListSerializer,
    ProductsDetailSerializer,
    
)

from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from ...filters import ProductFilter


# API مربوط به دسته‌بندی‌ها
class CategoryViewSet(ModelViewSet):

    # دریافت تمام دسته‌بندی‌ها از دیتابیس
    queryset = Category.objects.all()

    # انتخاب Serializer مناسب بر اساس نوع درخواست
    def get_serializer_class(self):

        # برای نمایش اطلاعات از Read استفاده می‌کنیم
        if self.action in ["list", "retrieve"]:
            return CategoryReadSerializer

        # برای ایجاد و ویرایش از Write استفاده می‌کنیم
        return CategoryWriteSerializer


# API مربوط به برندها
class BrandsViewSet(ModelViewSet):

    # دریافت تمام برندها از دیتابیس
    queryset = Brands.objects.all()

    # انتخاب Serializer مناسب بر اساس نوع درخواست
    def get_serializer_class(self):

        # برای نمایش اطلاعات از Read استفاده می‌کنیم
        if self.action in ["list", "retrieve"]:
            return BrandsReadSerializer

        # برای ایجاد و ویرایش از Write استفاده می‌کنیم
        return BrandsWriteSerializer
class ProductQuerysetMixin:
    def get_queryset(self):
        return (
            Products.objects
            .filter(is_active=True)
            .select_related("brand", "discount")
            .prefetch_related(
                "categories",
                Prefetch(
                    "product_images_set",
                    queryset=Product_Images.objects.all(),
                ),
                Prefetch(
                    "product_variants_set",
                    queryset=Product_Variants.objects.filter(
                        is_active=True
                    ),
                ),
            )
        )


class ProductListView(ProductQuerysetMixin, generics.ListAPIView):
    serializer_class = ProductsListSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_class = ProductFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]


class ProductDetailView(
    ProductQuerysetMixin,
    generics.RetrieveAPIView,):
    
    
    serializer_class = ProductsDetailSerializer
    lookup_field = "pk"