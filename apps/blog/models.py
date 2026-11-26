from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class Post(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    thumbnail = models.ImageField(
        upload_to="posts/thumbnails/",
        max_length=500,
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(default=False, db_index=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["author"], name="post_author_idx"),
        ]

    def __str__(self):
        return self.title


class Comment(TimeStampedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post"], name="comment_post_idx"),
            models.Index(fields=["user"], name="comment_user_idx"),
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.post}"
