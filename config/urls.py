"""
URL configuration for config project.
"""

from django.contrib import admin

from django.urls import include,path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    path('api/catalog/', include('apps.catalog.api.urls')),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # JWT Authentication
    path(
        "api/token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path(
        "api/token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "api/token/logout/",
        TokenBlacklistView.as_view(),
        name="token_blacklist",
    ),
    
    path("api/accounts/", include("apps.accounts.api.urls")),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("apps.accounts.api.urls")),
    path("api/catalog/", include("apps.catalog.api.urls")),
    path("api/cart/", include("apps.carts.api.urls")),
    path("api/blog/", include("apps.blog.api.urls")),
]
