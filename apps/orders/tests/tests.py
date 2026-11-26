from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Address
from apps.carts.models import Cart, CartItem
from apps.catalog.models import (
    Brand,
    Category,
    Discount,
    DiscountType,
    Product,
    ProductVariant,
)
from apps.orders.models import Order, OrderItem, Payment

User = get_user_model()


class OrderAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user1@example.com",
            password="StrongPass123!",
            phone="09120000001",
        )
        self.other = User.objects.create_user(
            email="user2@example.com",
            password="StrongPass123!",
            phone="09120000002",
        )
        self.address = Address.objects.create(
            user=self.user,
            province="Tehran",
            city="Tehran",
            address="Test address",
            postal_code="1234567890",
        )
        self.other_address = Address.objects.create(
            user=self.other,
            province="Shiraz",
            city="Shiraz",
            address="Other address",
            postal_code="9876543210",
        )

        category = Category.objects.create(name="Tools", slug="tools")
        brand = Brand.objects.create(name="Acme", slug="acme")
        discount_type = DiscountType.objects.create(name="Percent")
        discount = Discount.objects.create(
            discount="No discount", value=0, type=discount_type
        )
        self.product = Product.objects.create(
            name="Drill",
            slug="drill",
            brand=brand,
            discount=discount,
        )
        self.product.categories.add(category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="DRILL-001",
            price=Decimal("100.00"),
            stock=10,
        )

        self.order = Order.objects.create(
            user=self.user,
            address=self.address,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        self.paid_order = Order.objects.create(
            user=self.user,
            address=self.address,
            status=Order.Status.PROCESSING,
            payment_status=Order.PaymentStatus.PAID,
            subtotal=Decimal("200.00"),
            total_price=Decimal("200.00"),
        )
        self.other_order = Order.objects.create(
            user=self.other,
            address=self.other_address,
            subtotal=Decimal("300.00"),
            total_price=Decimal("300.00"),
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            variant=self.variant,
            product_name=self.product.name,
            unit_price=Decimal("100.00"),
            quantity=1,
            total_price=Decimal("100.00"),
        )

        self.list_url = reverse("order-list")
        self.client.force_authenticate(self.user)


class OrderListTests(OrderAPITestCase):
    def test_user_lists_only_own_orders(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(self.order.pk, ids)
        self.assertNotIn(self.other_order.pk, ids)

    def test_filter_by_status(self):
        response = self.client.get(self.list_url, {"status": "pending"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_retrieve_own_order_with_nested_items(self):
        response = self.client.get(
            reverse("order-detail", args=[self.order.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)

    def test_cannot_retrieve_other_users_order(self):
        response = self.client.get(
            reverse("order-detail", args=[self.other_order.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_authentication_is_required(self):
        self.client.force_authenticate(None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CancelOrderTests(OrderAPITestCase):
    def cancel(self, order):
        return self.client.post(reverse("order-cancel", args=[order.pk]))

    def test_cancel_restores_stock(self):
        initial_stock = self.variant.stock
        response = self.cancel(self.order)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)
        self.assertEqual(self.variant.stock, initial_stock + 1)

    def test_paid_order_cannot_be_cancelled(self):
        response = self.cancel(self.paid_order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_other_users_order_cannot_be_cancelled(self):
        response = self.cancel(self.other_order)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancelled_order_cannot_be_cancelled_again(self):
        self.order.status = Order.Status.CANCELLED
        self.order.save(update_fields=["status"])
        response = self.cancel(self.order)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rollback_when_save_fails(self):
        initial_stock = self.variant.stock
        with patch.object(Order, "save", side_effect=RuntimeError("failed")):
            with self.assertRaises(RuntimeError):
                self.cancel(self.order)

        self.variant.refresh_from_db()
        self.order.refresh_from_db()
        self.assertEqual(self.variant.stock, initial_stock)
        self.assertEqual(self.order.status, Order.Status.PENDING)


class CreateOrderTests(OrderAPITestCase):
    def setUp(self):
        super().setUp()
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            variant=self.variant,
            quantity=2,
        )

    def create_order(self, address=None):
        return self.client.post(
            self.list_url,
            {"address": (address or self.address).pk},
            format="json",
        )

    def test_creates_order_snapshot_payment_and_deducts_stock(self):
        response = self.create_order()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(pk=response.data["order_id"])
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, Decimal("200.00"))

        item = order.items.get()
        self.assertEqual(item.product_name, "Drill")
        self.assertEqual(item.unit_price, Decimal("100.00"))
        self.assertEqual(item.quantity, 2)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)
        self.assertEqual(self.cart.items.count(), 0)
        self.assertEqual(order.payments.get().method, Payment.Method.ONLINE)

    def test_rejects_foreign_address(self):
        response = self.create_order(self.other_address)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_empty_cart(self):
        self.cart.items.all().delete()
        response = self.create_order()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_insufficient_stock_without_side_effects(self):
        self.variant.stock = 1
        self.variant.save(update_fields=["stock"])

        response = self.create_order()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 1)
        self.assertEqual(self.cart.items.count(), 1)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 2)
