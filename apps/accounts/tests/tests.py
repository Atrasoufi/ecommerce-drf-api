from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Address, normalize_phone

User = get_user_model()


class NormalizePhoneTests(APITestCase):
    def test_normalizes_international_and_spaced_numbers(self):
        self.assertEqual(normalize_phone("+98 912 123 4567"), "09121234567")
        self.assertEqual(normalize_phone("0098-912-123-4567"), "09121234567")
        self.assertEqual(normalize_phone("989121234567"), "09121234567")

    def test_rejects_invalid_number(self):
        with self.assertRaises(ValueError):
            normalize_phone("12345")

    def test_create_user_rejects_empty_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="StrongPass123!",
                phone="09120000001",
            )


class RegistrationAPITests(APITestCase):
    url = reverse("user-list")

    def test_registers_user_with_hashed_password(self):
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "phone": "+98 912 000 0001",
                "password": "StrongPass123!",
                "password1": "StrongPass123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.phone, "09120000001")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertNotIn("password", response.data)

    def test_rejects_mismatched_password(self):
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "phone": "09120000001",
                "password": "StrongPass123!",
                "password1": "Different123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password1", response.data)

    def test_rejects_duplicate_phone(self):
        User.objects.create_user(
            email="old@example.com",
            password="StrongPass123!",
            phone="09120000001",
        )
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "phone": "09120000001",
                "password": "StrongPass123!",
                "password1": "StrongPass123!",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)


class AddressAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            phone="09120000001",
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            phone="09120000002",
        )
        self.list_url = reverse("address-list")
        self.client.force_authenticate(self.user)

    def create_address(self, **overrides):
        data = {
            "province": "Tehran",
            "city": "Tehran",
            "address": "Main street 1",
            "postal_code": "1234567890",
        }
        data.update(overrides)
        return self.client.post(self.list_url, data, format="json")

    def test_user_sees_only_own_addresses(self):
        own = self.create_address().data
        Address.objects.create(
            user=self.other,
            province="Shiraz",
            city="Shiraz",
            address="Other street",
            postal_code="9876543210",
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["results"]
        self.assertEqual([item["id"] for item in results], [own["id"]])

    def test_user_cannot_update_another_users_address(self):
        foreign = Address.objects.create(
            user=self.other,
            province="Shiraz",
            city="Shiraz",
            address="Other street",
            postal_code="9876543210",
        )
        url = reverse("address-detail", args=[foreign.pk])
        response = self.client.patch(url, {"city": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_set_default_is_atomic_and_revokes_previous_default(self):
        first = self.create_address(city="Tehran").data["id"]
        second = self.create_address(
            city="Mashhad", address="Second street"
        ).data["id"]

        self.client.post(reverse("address-set-default", args=[first]))
        self.client.post(reverse("address-set-default", args=[second]))

        self.assertFalse(Address.objects.get(pk=first).is_default)
        self.assertTrue(Address.objects.get(pk=second).is_default)

    def test_set_default_rejects_foreign_address(self):
        foreign = Address.objects.create(
            user=self.other,
            province="Shiraz",
            city="Shiraz",
            address="Other street",
            postal_code="9876543210",
        )
        response = self.client.post(
            reverse("address-set-default", args=[foreign.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            phone="09120000001",
        )
        self.url = reverse("user-me")

    def test_profile_requires_authentication(self):
        self.assertEqual(
            self.client.get(self.url).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_update_own_profile(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            self.url, {"phone": "09129999999"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "09129999999")
