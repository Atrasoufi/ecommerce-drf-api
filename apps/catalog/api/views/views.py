from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from ...models import Category, Brands
from ..serializers.seralizers import (
    CategoryReadSerializer,
    CategoryWriteSerializer,
    BrandsReadSerializer,
    BrandsWriteSerializer,
)


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
