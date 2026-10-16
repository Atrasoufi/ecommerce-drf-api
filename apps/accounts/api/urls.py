
from django.urls import path

from apps.accounts.api.views.views import ProfileView

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
]
