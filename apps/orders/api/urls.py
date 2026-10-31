from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.orders.api.views.views import (
    OrderViewSet,
    CancelOrderAPIView,
)

router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path(
        "orders/<int:pk>/cancel/",
        CancelOrderAPIView.as_view(),
        name="order-cancel",
    ),
    path("", include(router.urls)),
]