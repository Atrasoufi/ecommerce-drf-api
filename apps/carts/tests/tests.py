from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.carts.models import Cart, CartItem
from apps.catalog.models import Brand, Category, Product, ProductVariant

User = get_user_model()


class CartAPITestCase(APITestCase):
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
        category = Category.objects.create(name="Tools", slug="tools")
        brand = Brand.objects.create(name="Acme", slug="acme")
        self.product = Product.objects.create(
            name="Hammer", slug="hammer", brand=brand
        )
        self.product.categories.add(category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="HAM-001",
            price=Decimal("10.00"),
            stock=5,
        )
        self.other_variant = ProductVariant.objects.create(
            product=self.product,
            sku="HAM-002",
            price=Decimal("12.00"),
            stock=3,
        )
        self.list_url = reverse("cart-item-list")
        self.client.force_authenticate(self.user)

    def add_item(self, quantity=1, variant=None):
        return self.client.post(
            self.list_url,
            {
                "product": self.product.pk,
                "variant": (variant or self.variant).pk,
                "quantity": quantity,
            },
            format="json",
        )

    def test_reading_cart_does_not_create_one(self):
        response = self.client.get(reverse("cart-detail"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Cart.objects.filter(user=self.user).exists())
        self.assertEqual(response.data["items"], [])

    def test_unauthenticated_access_is_rejected(self):
        self.client.force_authenticate(None)
        self.assertEqual(
            self.client.get(reverse("cart-detail")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_add_item_then_merge_quantity(self):
        first = self.add_item(2)
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        second = self.add_item(1)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        item = CartItem.objects.get(cart__user=self.user)
        self.assertEqual(item.quantity, 3)

    def test_stock_is_enforced_on_merge(self):
        self.add_item(4)
        response = self.add_item(2)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CartItem.objects.get(cart__user=self.user).quantity, 4)

    def test_inactive_variant_is_rejected(self):
        self.variant.is_active = False
        self.variant.save(update_fields=["is_active"])
        response = self.add_item(1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_changes_variant_and_quantity(self):
        self.add_item(1)
        item = CartItem.objects.get(cart__user=self.user)
        url = reverse("cart-item-detail", args=[item.pk])
        response = self.client.patch(
            url,
            {"variant": self.other_variant.pk, "quantity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.variant, self.other_variant)
        self.assertEqual(item.quantity, 2)

    def test_user_cannot_update_another_users_item(self):
        self.add_item(1)
        item = CartItem.objects.get(cart__user=self.user)
        self.client.force_authenticate(self.other)
        response = self.client.patch(
            reverse("cart-item-detail", args=[item.pk]),
            {"quantity": 9},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_item(self):
        self.add_item(1)
        item = CartItem.objects.get(cart__user=self.user)
        response = self.client.delete(
            reverse("cart-item-detail", args=[item.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CartItem.objects.filter(pk=item.pk).exists())
