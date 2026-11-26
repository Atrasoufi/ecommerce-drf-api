from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.blog.models import Comment, Post

User = get_user_model()


class CommentAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            phone="09123456789",
            password="StrongPass123!",
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            phone="09123456780",
            password="StrongPass123!",
            is_staff=True,
        )
        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            slug="test-post",
            content="Test post content",
            is_published=True,
        )
        self.approved = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Approved comment",
            is_approved=True,
        )
        self.pending = Comment.objects.create(
            post=self.post,
            user=self.user,
            content="Pending comment",
        )
        self.list_url = reverse("comment-list")

    def test_list_shows_only_approved_comments(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.approved.pk, ids)
        self.assertNotIn(self.pending.pk, ids)

    def test_authenticated_user_can_create_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.list_url,
            {"post": self.post.pk, "content": "A new comment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.user.email)
        self.assertFalse(response.data["is_approved"])
        self.assertTrue(
            Comment.objects.filter(
                post=self.post, user=self.user, content="A new comment"
            ).exists()
        )

    def test_anonymous_user_cannot_create_comment(self):
        response = self.client.post(
            self.list_url,
            {"post": self.post.pk, "content": "Anonymous"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_can_approve_and_reject(self):
        self.client.force_authenticate(self.staff)
        approve_url = reverse("comment-approve", args=[self.pending.pk])
        reject_url = reverse("comment-reject", args=[self.approved.pk])

        self.assertEqual(
            self.client.post(approve_url).status_code, status.HTTP_200_OK
        )
        self.pending.refresh_from_db()
        self.assertTrue(self.pending.is_approved)

        self.assertEqual(
            self.client.post(reject_url).status_code, status.HTTP_200_OK
        )
        self.approved.refresh_from_db()
        self.assertFalse(self.approved.is_approved)

    def test_regular_user_cannot_moderate(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse("comment-approve", args=[self.pending.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete_own_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.delete(
            reverse("comment-detail", args=[self.pending.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_other_user_cannot_delete_comment(self):
        other = User.objects.create_user(
            email="other@example.com",
            phone="09123456781",
            password="StrongPass123!",
        )
        self.client.force_authenticate(other)
        response = self.client.delete(
            reverse("comment-detail", args=[self.pending.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authenticated_user_can_retrieve_own_pending_comment(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse("comment-detail", args=[self.pending.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PostAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="author@example.com",
            phone="09123456782",
            password="StrongPass123!",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            phone="09123456783",
            password="StrongPass123!",
        )
        self.list_url = reverse("post-list")

    def test_anonymous_sees_only_published_posts(self):
        Post.objects.create(
            author=self.user,
            title="Draft",
            slug="draft",
            content="Draft",
        )
        Post.objects.create(
            author=self.user,
            title="Live",
            slug="live",
            content="Live",
            is_published=True,
        )
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item["title"] for item in response.data["results"]]
        self.assertEqual(titles, ["Live"])

    def test_create_generates_unique_slug_and_published_at(self):
        self.client.force_authenticate(self.user)
        payload = {
            "title": "Hello World",
            "content": "Body",
            "is_published": True,
        }
        first = self.client.post(self.list_url, payload, format="json")
        second = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(first.data["slug"], second.data["slug"])
        self.assertIsNotNone(first.data["published_at"])
        self.assertEqual(first.data["author"], self.user.email)

    def test_other_user_cannot_edit_post(self):
        post = Post.objects.create(
            author=self.user,
            title="Original",
            slug="original",
            content="Body",
            is_published=True,
        )
        self.client.force_authenticate(self.other)
        response = self.client.patch(
            reverse("post-detail", args=[post.pk]),
            {"title": "Changed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_publishing_post_sets_published_at(self):
        post = Post.objects.create(
            author=self.user,
            title="Draft",
            slug="draft",
            content="Body",
        )
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse("post-detail", args=[post.pk]),
            {"is_published": True},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertIsNotNone(post.published_at)
