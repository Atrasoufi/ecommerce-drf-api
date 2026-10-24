
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from blog.models import Post


class PostModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="test-password",
        )

    def test_slug_must_be_unique(self):
        Post.objects.create(
            author=self.user,
            title="First post",
            slug="same-slug",
            content="First content",
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(
                    author=self.user,
                    title="Second post",
                    slug="same-slug",
                    content="Second content",
                )

