from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Address
from apps.catalog.models import (
    Category,
    Discount,
    Discount_Type,
    Product_Variants,
    Products,
)
from apps.orders.models import Order, OrderItem
from apps.carts.models import Cart, CartItem
from apps.orders.models import Payment


User = get_user_model()


class OrderAPITestCase(TestCase):
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
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]
        return response.data

    # Task #38: list, retrieve, ownership, authentication, and filtering.

    def test_user_can_list_own_orders(self):
        self.authenticate()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(self.get_results(response)), 2)

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

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    # Task #39: cancellation validation, stock restoration, and rollback.

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
        self.assertEqual(self.variant.stock, initial_stock + 1)

    def test_user_can_cancel_processing_unpaid_order(self):
        self.authenticate()
        self.order1.status = Order.Status.PROCESSING
        self.order1.save(update_fields=["status"])
        initial_stock = self.variant.stock

        response = self.client.post(
            f"{self.list_url}{self.order1.id}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(self.order1.status, Order.Status.CANCELLED)
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
        self.assertEqual(self.order2.status, Order.Status.PROCESSING)

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

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_stock_restoration_rolls_back_if_order_save_fails(self):
        self.authenticate()
        initial_stock = self.variant.stock

        with patch.object(Order, "save", side_effect=RuntimeError("save failed")):
            with self.assertRaises(RuntimeError):
                self.client.post(
                    f"{self.list_url}{self.order1.id}/cancel/"
                )

        self.order1.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(self.order1.status, Order.Status.PENDING)
        self.assertEqual(self.variant.stock, initial_stock)
class CreateOrderTestCase(OrderAPITestCase):
    # آدرس endpoint ساخت سفارش
    create_url = "/api/orders/create/"

    def setUp(self):
        super().setUp()

        # ساخت سبد خرید برای کاربر
        self.cart = Cart.objects.create(user=self.user1)

        # اضافه کردن محصول به سبد خرید
        CartItem.objects.create(
            cart=self.cart,
            product=self.variant.product,
            variant=self.variant,
            quantity=2,
        )

    def test_user_can_create_order_from_cart(self):
        # احراز هویت کاربر
        self.authenticate()

        # ثبت سفارش با آدرس متعلق به کاربر
        response = self.client.post(
            self.create_url,
            {"address": self.address1.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # بررسی ایجاد سفارش
        order = Order.objects.get(id=response.data["order_id"])
        self.assertEqual(order.user, self.user1)
        self.assertEqual(order.total_price, Decimal("200.00"))

        # بررسی ذخیره اطلاعات محصول در OrderItem
        order_item = order.items.first()
        self.assertEqual(order_item.product_name, "Test Product")
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, Decimal("100.00"))

        # بررسی کاهش موجودی از 10 به 8
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock, 8)

        # بررسی خالی شدن سبد خرید
        self.assertEqual(self.cart.items.count(), 0)

        # بررسی ایجاد پرداخت اولیه
        payment = order.payments.first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.method, Payment.Method.ONLINE)
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_user_cannot_order_using_another_users_address(self):
        # احراز هویت کاربر اول
        self.authenticate()

        # تلاش برای استفاده از آدرس کاربر دوم
        response = self.client.post(
            self.create_url,
            {"address": self.address2.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_create_order_with_empty_cart(self):
        # حذف آیتم‌های سبد خرید
        self.cart.items.all().delete()

        self.authenticate()

        response = self.client.post(
            self.create_url,
            {"address": self.address1.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_create_order_with_insufficient_stock(self):
    # موجودی را کمتر از تعداد درخواستی سبد خرید قرار می‌دهیم
       self.variant.stock = 1
       self.variant.save(update_fields=["stock"])

       self.authenticate()

    # تلاش برای ثبت سفارش با موجودی ناکافی
       response = self.client.post(
           self.create_url,
           {"address": self.address1.id},
           format="json",
    )

    # سفارش نباید ثبت شود
       self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # موجودی نباید تغییر کند
       self.variant.refresh_from_db()
       self.assertEqual(self.variant.stock, 1)

    # سبد خرید باید حفظ شود
       self.assertEqual(self.cart.items.count(), 1)

    # هیچ سفارش جدیدی نباید ساخته شود
       self.assertEqual(
           Order.objects.filter(user=self.user1).count(),
        2,
    )