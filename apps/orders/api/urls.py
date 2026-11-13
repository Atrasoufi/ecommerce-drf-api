from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.orders.api.views.views import (
    CancelOrderAPIView,
    CreateOrderAPIView,
    OrderViewSet,
)


router = DefaultRouter()
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path(
        "orders/<int:pk>/cancel/",
        CancelOrderAPIView.as_view(),
        name="order-cancel",
    ),
    path("create/", CreateOrderAPIView.as_view(), name="create-order"),
    path("", include(router.urls)),
]
