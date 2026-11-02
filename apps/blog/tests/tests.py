from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Comment, Post

User = get_user_model()


class CommentAPITests(APITestCase):
    """Tests for the Comment API endpoints."""

    def setUp(self):
        # Create a regular user and a staff user.
        self.user = User.objects.create_user(
            email="user@example.com",
            phone="09123456789",
            password="test-password",
        )
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            phone="09123456780",
            password="test-password",
            is_staff=True,
        )

        # Create a post for the comment tests.
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            slug="test-post",
            content="Test post content",
            is_published=True,
        )

        # Create approved and pending comments.
        self.approved_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Approved comment",
            is_approved=True,
        )
        self.pending_comment = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Pending comment",
            is_approved=False,
        )

        # Define the API endpoint URLs.
        self.comment_list_url = reverse("comment-list")
        self.approve_url = reverse(
            "comment-approve",
            kwargs={"pk": self.pending_comment.pk},
        )
        self.reject_url = reverse(
            "comment-reject",
            kwargs={"pk": self.approved_comment.pk},
        )

    def test_list_shows_only_approved_comments(self):
        # Public users should only see approved comments.
        response = self.client.get(self.comment_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [item["id"] for item in response.data]
        self.assertIn(self.approved_comment.id, returned_ids)
        self.assertNotIn(self.pending_comment.id, returned_ids)

    def test_authenticated_user_can_create_comment(self):
        # Authenticated users can submit comments for moderation.
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comment_list_url,
            {
                "post": self.post.id,
                "content": "A new comment",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.id)
        self.assertFalse(response.data["is_approved"])
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                user=self.user,
                content="A new comment",
                is_approved=False,
            ).exists()
        )

    def test_anonymous_user_cannot_create_comment(self):
        # Anonymous users must authenticate before commenting.
        response = self.client.post(
            self.comment_list_url,
            {
                "post": self.post.id,
                "content": "An anonymous comment",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_staff_can_approve_comment(self):
        # Staff users can approve pending comments.
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(self.approve_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending_comment.refresh_from_db()
        self.assertTrue(self.pending_comment.is_approved)

    def test_staff_can_reject_comment(self):
        # Staff users can reject approved comments.
        self.client.force_authenticate(user=self.staff_user)

        response = self.client.post(self.reject_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.approved_comment.refresh_from_db()
        self.assertFalse(self.approved_comment.is_approved)

    def test_regular_user_cannot_approve_comment(self):
        # Regular users must not be allowed to moderate comments.
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.approve_url)

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_author_can_delete_own_comment(self):
        # A comment author can delete their own comment.
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            reverse(
                "comment-detail",
                kwargs={"pk": self.pending_comment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Comment.objects.filter(pk=self.pending_comment.pk).exists()
        )

    def test_user_cannot_delete_another_users_comment(self):
        # Users must not delete comments written by other users.
        other_user = User.objects.create_user(
            email="other@example.com",
            phone="09123456781",
            password="test-password",
        )
        self.client.force_authenticate(user=other_user)

        response = self.client.delete(
            reverse(
                "comment-detail",
                kwargs={"pk": self.pending_comment.pk},
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_blank_comment_is_rejected(self):
        # Comments containing only whitespace must be rejected.
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.comment_list_url,
            {
                "post": self.post.id,
                "content": "   ",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
