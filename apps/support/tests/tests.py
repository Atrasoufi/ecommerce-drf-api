from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.support.models import ContactMessage, FAQ

User = get_user_model()


class FAQAPITests(APITestCase):
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
        self.active = FAQ.objects.create(
            question="Active?", answer="Yes", display_order=1
        )
        self.inactive = FAQ.objects.create(
            question="Hidden?", answer="No", is_active=False, display_order=2
        )
        self.list_url = reverse("faq-list")

    def test_public_sees_only_active_faqs(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [self.active.pk])

    def test_staff_sees_all_faqs(self):
        self.client.force_authenticate(self.staff)
        response = self.client.get(self.list_url)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.inactive.pk, ids)

    def test_regular_user_cannot_create_faq(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.list_url, {"question": "Q", "answer": "A"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_faq(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            self.list_url,
            {"question": "New?", "answer": "New answer"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ContactMessageAPITests(APITestCase):
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
        self.list_url = reverse("contactmessage-list")
        self.payload = {
            "name": "Visitor",
            "email": "visitor@example.com",
            "subject": "Question",
            "message": "How can I help?",
        }

    def test_anonymous_user_can_submit_message(self):
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        message = ContactMessage.objects.get()
        self.assertIsNone(message.user)
        self.assertFalse(message.is_read)

    def test_authenticated_user_is_attached_to_message(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.get().user, self.user)

    def test_only_staff_can_list_messages(self):
        ContactMessage.objects.create(**self.payload)
        self.assertIn(
            self.client.get(self.list_url).status_code,
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )

        self.client.force_authenticate(self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
