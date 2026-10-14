from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.catalog.api.views.review import ReviewViewSet
from apps.catalog.api.views.favorite import FavoriteViewSet

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

urlpatterns = [
    path('', include(router.urls)),
]