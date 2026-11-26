from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.catalog.models import (
    Brand,
    Category,
    Discount,
    DiscountType,
    Favorite,
    Product,
    ProductVariant,
    Review,
)

User = get_user_model()


class CatalogAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="StrongPass123!",
            phone="09120000001",
        )
        self.staff = User.objects.create_user(
            email="staff@example.com",
            password="StrongPass123!",
            phone="09120000002",
            is_staff=True,
        )
        self.category = Category.objects.create(
            name="Electronics", slug="electronics"
        )
        self.brand = Brand.objects.create(name="Acme", slug="acme")
        discount_type = DiscountType.objects.create(name="Percent")
        self.discount = Discount.objects.create(
            discount="No discount", value=0, type=discount_type
        )
        self.product = Product.objects.create(
            name="Laptop",
            slug="laptop",
            brand=self.brand,
            discount=self.discount,
        )
        self.product.categories.add(self.category)
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku="LAP-001",
            color="Black",
            warranty="12 months",
            price=Decimal("100.00"),
            stock=10,
        )


class CategoryAndBrandPermissionTests(CatalogAPITestCase):
    def test_anonymous_cannot_write_categories(self):
        response = self.client.post(
            reverse("category-list"), {"name": "New", "slug": "new"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_write_categories_or_brands(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(
            self.client.post(
                reverse("category-list"), {"name": "New", "slug": "new"}
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.post(
                reverse("brand-list"), {"name": "New", "slug": "new"}
            ).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_staff_can_create_category(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            reverse("category-list"),
            {"name": "Phones", "slug": "phones", "description": "Mobile"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(slug="phones").exists())

    def test_product_detail_is_available_to_anonymous_users(self):
        response = self.client.get(
            reverse("product-detail", args=[self.product.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Laptop")
        self.assertEqual(len(response.data["variants"]), 1)


class ProductFilterTests(CatalogAPITestCase):
    def test_filters_by_category_and_min_price(self):
        expensive = Product.objects.create(
            name="Pro", slug="pro", brand=self.brand
        )
        expensive.categories.add(self.category)
        ProductVariant.objects.create(
            product=expensive,
            sku="PRO-001",
            price=Decimal("500.00"),
            stock=1,
        )

        url = reverse("product-list")
        response = self.client.get(
            url,
            {
                "category": self.category.pk,
                "min_price": "200",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["Pro"])


class ReviewPermissionTests(CatalogAPITestCase):
    def setUp(self):
        super().setUp()
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=4,
            comment="Good",
            is_approved=True,
        )
        self.other = User.objects.create_user(
            email="other@example.com",
            password="StrongPass123!",
            phone="09120000003",
        )

    def test_anonymous_can_read_approved_reviews(self):
        response = self.client.get(reverse("review-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_owner_can_update_own_review(self):
        self.client.force_authenticate(self.user)
        response = self.client.patch(
            reverse("review-detail", args=[self.review.pk]),
            {"comment": "Updated"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.comment, "Updated")

    def test_other_user_cannot_update_review(self):
        self.client.force_authenticate(self.other)
        response = self.client.patch(
            reverse("review-detail", args=[self.review.pk]),
            {"comment": "Hijacked"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_staff_can_moderate_review(self):
        self.client.force_authenticate(self.staff)
        response = self.client.patch(
            reverse("review-detail", args=[self.review.pk]),
            {"rating": 5},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)


class FavoritePermissionTests(CatalogAPITestCase):
    def test_user_sees_only_own_favorites(self):
        Favorite.objects.create(user=self.user, product=self.product)
        other_product = Product.objects.create(
            name="Other", slug="other", brand=self.brand
        )
        Favorite.objects.create(user=self.staff, product=other_product)

        self.client.force_authenticate(self.user)
        response = self.client.get(reverse("favorite-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["product_name"], "Laptop")
