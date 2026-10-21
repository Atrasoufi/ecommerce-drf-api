from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.catalog.api.views.review import ReviewViewSet
from apps.catalog.api.views.favorite import FavoriteViewSet
from .views.views import (
    CategoryViewSet,
    BrandsViewSet,
    ProductListView,
    ProductDetailView,
)

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
    path("category/", CategoryViewSet.as_view({"get": "list", "post": "create"}),name="category"),
    path("brand/", BrandsViewSet.as_view({"get": "list", "post": "create"}),name="brand"),
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]