from django.urls import path
from .views.views import RegistrationAPIView

urlpatterns = [
    path(
        "register/",
        RegistrationAPIView.as_view(),
        name="register",
    ),
]
