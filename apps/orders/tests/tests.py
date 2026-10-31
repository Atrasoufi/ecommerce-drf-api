from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Address
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
    """
    API tests for Order List/Retrieve (#38) and Cancel Order (#39).

    Endpoint paths below match the current urls.py configuration:
    /api/orders/orders/
    /api/orders/orders/<id>/
    /api/orders/orders/<id>/cancel/
    """

    list_url = "/api/orders/orders/"

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

        self.address1 = Address.objects.create(
            user=self.user1,
            province="Tehran",
            city="Tehran",
            address="Test Address 1",
            postal_code="1234567890",
        )
        self.address2 = Address.objects.create(
            user=self.user2,
            province="Tehran",
            city="Tehran",
            address="Test Address 2",
            postal_code="1234567891",
        )

        discount_type = Discount_Type.objects.create(name="Percentage")
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

        self.variant = Product_Variants.objects.create(
            product=product,
            sku="TEST-001",
            color="Black",
            warranty="TEST-WARRANTY-001",
            price=Decimal("100.00"),
            stock=10,
        )

        self.order1 = Order.objects.create(
            user=self.user1,
            address=self.address1,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=Decimal("100.00"),
            total_price=Decimal("100.00"),
        )
        self.order2 = Order.objects.create(
            user=self.user1,
            address=self.address1,
            status=Order.Status.PROCESSING,
            payment_status=Order.PaymentStatus.PAID,
            subtotal=Decimal("200.00"),
            total_price=Decimal("200.00"),
        )
        self.other_user_order = Order.objects.create(
            user=self.user2,
            address=self.address2,
            status=Order.Status.PENDING,
            payment_status=Order.PaymentStatus.PENDING,
            subtotal=Decimal("300.00"),
            total_price=Decimal("300.00"),
        )

        self.order_item = OrderItem.objects.create(
            order=self.order1,
            product=product,
            variant=self.variant,
            product_name="Test Product",
            unit_price=Decimal("100.00"),
            quantity=1,
            total_price=Decimal("100.00"),
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user1)

    @staticmethod
    def get_results(response):
        """Support both paginated and non-paginated list responses."""
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    # Issue #38: Order List & Retrieve

    def test_user_can_list_own_orders(self):
        self.authenticate()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        orders = self.get_results(response)
        self.assertEqual(len(orders), 2)

    def test_user_cannot_see_other_users_orders(self):
        self.authenticate()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_ids = [order["id"] for order in self.get_results(response)]
        self.assertNotIn(self.other_user_order.id, order_ids)

    def test_filter_orders_by_status(self):
        self.authenticate()

        response = self.client.get(self.list_url, {"status": "pending"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        orders = self.get_results(response)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0]["status"], Order.Status.PENDING)

    def test_user_can_retrieve_own_order(self):
        self.authenticate()

        response = self.client.get(f"{self.list_url}{self.order1.id}/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["payment_status"],
            Order.PaymentStatus.PENDING,
        )
        self.assertEqual(len(response.data["items"]), 1)

    def test_user_cannot_retrieve_other_users_order(self):
        self.authenticate()

        response = self.client.get(
            f"{self.list_url}{self.other_user_order.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_user_cannot_list_orders(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Issue #39: Cancel Order

    def test_user_can_cancel_pending_unpaid_order(self):
        self.authenticate()
        initial_stock = self.variant.stock

        response = self.client.post(
            f"{self.list_url}{self.order1.id}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.order1.refresh_from_db()
        self.variant.refresh_from_db()

        self.assertEqual(self.order1.status, Order.Status.CANCELLED)
        self.assertEqual(
            self.order1.payment_status,
            Order.PaymentStatus.PENDING,
        )
        self.assertEqual(self.variant.stock, initial_stock + 1)

    def test_user_cannot_cancel_paid_order(self):
        self.authenticate()

        response = self.client.post(
            f"{self.list_url}{self.order2.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.order2.refresh_from_db()
        self.assertEqual(
            self.order2.status,
            Order.Status.PROCESSING,
        )

    def test_user_cannot_cancel_other_users_order(self):
        self.authenticate()

        response = self.client.post(
            f"{self.list_url}{self.other_user_order.id}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_cancel_already_cancelled_order(self):
        self.authenticate()
        self.order1.status = Order.Status.CANCELLED
        self.order1.save(update_fields=["status"])

        initial_stock = self.variant.stock

        response = self.client.post(
            f"{self.list_url}{self.order1.id}/cancel/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, initial_stock)

    def test_unauthenticated_user_cannot_cancel_order(self):
        response = self.client.post(
            f"{self.list_url}{self.order1.id}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
