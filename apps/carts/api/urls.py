from django.urls import path
from .views.views import CartView, CartItemViewSet

cart_item_list = CartItemViewSet.as_view({
    "get": "list",
    "post": "create",
})

cart_item_detail = CartItemViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})


urlpatterns = [
    path("", CartView.as_view(), name="cart-detail"),

    path(
        "items/",
        cart_item_list,
        name="cart-item-list",
    ),

    path(
        "items/<int:pk>/",
        cart_item_detail,
        name="cart-item-detail",
    ),
]
