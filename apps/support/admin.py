from django.contrib import admin
from .models import FAQ, ContactMessage


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = (
        "question",
        "is_active",
        "display_order",
        "created_at",
    )
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("display_order",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "name",
        "email",
        "is_read",
        "created_at",
    )
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    list_editable = ("is_read",)
