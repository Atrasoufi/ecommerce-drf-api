from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContactMessageViewSet, FAQViewSet

router = DefaultRouter()
router.register(r"faqs", FAQViewSet, basename="faq")
router.register(
    r"contact-messages", ContactMessageViewSet, basename="contactmessage"
)

urlpatterns = [path("", include(router.urls))]
