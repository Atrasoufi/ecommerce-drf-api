from django.urls import path
from .views.views import FAQViewSet

faq_list = FAQViewSet.as_view({
    "get": "list",
    "post": "create",
})

faq_detail = FAQViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("faqs/", faq_list, name="faq-list"),
    path("faqs/<int:pk>/", faq_detail, name="faq-detail"),
]