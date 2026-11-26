from django.db.models import Prefetch

from apps.catalog.models import (
    Brand,
    Category,
    Favorite,
    Product,
    ProductImage,
    ProductVariant,
    Review,
)


def get_product_queryset(*, include_inactive=False):
    """Return a product queryset without N+1 queries for nested serializers."""
    products = Product.objects.all()
    if not include_inactive:
        products = products.filter(is_active=True)

    return (
        products.select_related("brand", "discount")
        .prefetch_related(
            "categories",
            Prefetch("images", queryset=ProductImage.objects.all()),
            Prefetch(
                "variants",
                queryset=ProductVariant.objects.filter(is_active=True),
            ),
        )
        .distinct()
    )


def get_category_queryset():
    return Category.objects.all()


def get_brand_queryset():
    return Brand.objects.all()


def get_review_queryset(*, user=None):
    """Staff see every review; other users only approved ones."""
    queryset = Review.objects.select_related("user", "product")
    if user and user.is_authenticated and user.is_staff:
        return queryset
    return queryset.filter(is_approved=True)


def get_favorite_queryset(*, user):
    return Favorite.objects.filter(user=user).select_related("product", "user")


def get_review_write_queryset(*, user):
    """Restrict review modifications to the owner, or all rows for staff."""
    queryset = Review.objects.select_related("user", "product")
    if user.is_authenticated and user.is_staff:
        return queryset
    return queryset.filter(user=user)
