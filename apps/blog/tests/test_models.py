from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.blog.models import Comment, Post


User = get_user_model()


class PostModelTests(TestCase):
    """Tests for the Post model."""

    def setUp(self):
        # Create a user using the project's custom user model.
        self.user = User.objects.create_user(
            email="testuser@example.com",
            phone="09123456789",
            password="test-password",
        )

    def test_slug_must_be_unique(self):
        # Create the first post with a unique slug.
        Post.objects.create(
            author=self.user,
            title="First post",
            slug="same-slug",
            content="First content",
        )

        # Creating another post with the same slug must fail.
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(
                    author=self.user,
                    title="Second post",
                    slug="same-slug",
                    content="Second content",
                )


class CommentModelTests(TestCase):
    """Tests for the Comment model."""

    def setUp(self):
        # Create a user using the project's custom user model.
        self.user = User.objects.create_user(
            email="commenter@example.com",
            phone="09123456780",
            password="test-password",
        )

        # Create a post for the comment tests.
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            slug="test-post",
            content="Test post content",
        )

    def test_comment_is_unapproved_by_default(self):
        # New comments should require moderation by default.
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="This is a test comment.",
        )

        self.assertFalse(comment.is_approved)

    def test_comment_str_representation(self):
        # The string representation should include the user and post.
        comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="This is a test comment.",
        )

        self.assertEqual(
            str(comment),
            f"Comment by {self.user} on {self.post}",
        )
