from django.urls import path

from .views import (
    AddressDetailView,
    AddressListCreateView,
    ProfileView,
    RegistrationAPIView,
    SetDefaultAddressView,
)

urlpatterns = [
    path(
        "users/",
        RegistrationAPIView.as_view(),
        name="user-list",
    ),
    path(
        "users/me/",
        ProfileView.as_view(),
        name="user-me",
    ),
    path(
        "addresses/",
        AddressListCreateView.as_view(),
        name="address-list",
    ),
    path(
        "addresses/<int:pk>/",
        AddressDetailView.as_view(),
        name="address-detail",
    ),
    path(
        "addresses/<int:pk>/set-default/",
        SetDefaultAddressView.as_view(),
        name="address-set-default",
    ),
]
