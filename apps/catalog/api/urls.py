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
router.register(r'categories', CategoryViewSet, basename='category') # 
router.register(r'brands', BrandsViewSet, basename='brand')#
#
urlpatterns = [
    path('', include(router.urls)),
    
    path("products/", ProductListView.as_view(), name="product-list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="product-detail"),
]