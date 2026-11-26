from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.models import Comment, Post


def generate_unique_slug(title):
    """Build a unique slug from a post title."""
    base_slug = slugify(title) or "post"
    slug = base_slug
    counter = 1
    while Post.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


def get_post_queryset(*, user=None):
    """Return visible posts with authors preloaded for serialization."""
    queryset = Post.objects.select_related("author")
    if user and user.is_authenticated and user.is_staff:
        return queryset
    if user and user.is_authenticated:
        return queryset.filter(Q(is_published=True) | Q(author=user))
    return queryset.filter(is_published=True)


def get_comment_queryset():
    return Comment.objects.select_related("post", "user")


@transaction.atomic
def create_post(*, author, validated_data):
    data = dict(validated_data)
    data["slug"] = generate_unique_slug(data["title"])
    if data.get("is_published"):
        data["published_at"] = timezone.now()
    return Post.objects.create(author=author, **data)


@transaction.atomic
def update_post(*, instance, validated_data):
    data = dict(validated_data)
    if (
        data.get("is_published")
        and not instance.is_published
        and not instance.published_at
    ):
        data["published_at"] = timezone.now()

    for field, value in data.items():
        setattr(instance, field, value)
    instance.save()
    return instance


@transaction.atomic
def create_comment(*, user, validated_data):
    return Comment.objects.create(user=user, is_approved=False, **validated_data)


@transaction.atomic
def set_comment_approval(*, comment_pk, is_approved):
    comment = get_object_or_404(get_comment_queryset(), pk=comment_pk)
    comment.is_approved = is_approved
    comment.save(update_fields=["is_approved", "updated_at"])
    return comment
