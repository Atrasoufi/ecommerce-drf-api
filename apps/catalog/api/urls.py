from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BrandViewSet,
    CategoryViewSet,
    FavoriteViewSet,
    ProductViewSet,
    ReviewViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"brands", BrandViewSet, basename="brand")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"favorites", FavoriteViewSet, basename="favorite")

urlpatterns = [path("", include(router.urls))]
