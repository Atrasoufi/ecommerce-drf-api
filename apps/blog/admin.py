from django.contrib import admin

from .models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "is_published",
        "published_at",
        "created_at",
    )
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "slug", "content")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "user",
        "is_approved",
        "created_at",
    )
    list_filter = ("is_approved", "created_at")
    search_fields = ("content",)
