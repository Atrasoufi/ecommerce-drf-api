from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.views import CategoryViewSet, BrandsViewSet


# اتصال مسیرهای تولیدشده به URLهای اپلیکیشن
urlpatterns = [
    path("category/", CategoryViewSet.as_view({"get": "list", "post": "create"}),name="category"),
    path("brand/", BrandsViewSet.as_view({"get": "list", "post": "create"}),name="brand"),
]