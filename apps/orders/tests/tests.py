
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.orders.models import Order, OrderItem
from apps.catalog.models import (
    Category,
    Discount_Type,
    Discount,
    Products,
    Product_Variants,
)


User = get_user_model()


class OrderAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="TestPass123!",
            phone="09120000001",
        )

        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="TestPass123!",
            phone="09120000002",
        )

        discount_type = Discount_Type.objects.create(
            name="Percentage",
        )

        discount = Discount.objects.create(
            discount="No discount",
            value=0,
            type=discount_type,
        )

        category = Category.objects.create(
            name="Test Category",
            slug="test-category",
        )

        product = Products.objects.create(
            name="Test Product",
            slug="test-product",
            discount=discount,
        )
        product.categories.add(category)

        variant = Product_Variants.objects.create(
            product=product,
            sku="TEST-001",
            color="Black",
            warranty="TEST-WARRANTY-001",
            price=Decimal("100.00"),
            stock=10,
        )

        self.order1 = Order.objects.create(
            user=self.user1,
            status="pending",
            payment_status="unpaid",
            subtotal=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )

        self.order2 = Order.objects.create(
            user=self.user1,
            status="processing",
            payment_status="paid",
            subtotal=Decimal("200.00"),
            total_price=Decimal("200.00"),
        )

        self.other_user_order = Order.objects.create(
            user=self.user2,
            status="pending",
            total_price=Decimal("300.00"),
        )

        OrderItem.objects.create(
            order=self.order1,
            product=product,
            variant=variant,
            product_name="Test Product",
            unit_price=Decimal("100.00"),
            quantity=1,
            total_price=Decimal("100.00"),
        )

    def test_user_can_list_own_orders(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get("/api/orders/orders/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_user_cannot_see_other_users_orders(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get("/api/orders/orders/")

        order_ids = [order["id"] for order in response.data]

        self.assertNotIn(self.other_user_order.id, order_ids)

    def test_filter_orders_by_status(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            "/api/orders/orders/?status=pending"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["status"], "pending")

    def test_user_can_retrieve_own_order(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f"/api/orders/orders/{self.order1.id}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["payment_status"], "unpaid")
        self.assertEqual(len(response.data["items"]), 1)

    def test_user_cannot_retrieve_other_users_order(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(
            f"/api/orders/orders/{self.other_user_order.id}/"
        )

        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_user_cannot_list_orders(self):
        response = self.client.get("/api/orders/orders/")

        self.assertEqual(response.status_code, 401)
