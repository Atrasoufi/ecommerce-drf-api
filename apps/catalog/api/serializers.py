from rest_framework import serializers

from apps.catalog.models import (
    Brand,
    Category,
    Favorite,
    Product,
    ProductImage,
    ProductVariant,
    Review,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "is_active"]
        read_only_fields = ["id"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "logo", "is_active"]
        read_only_fields = ["id"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "image", "is_primary"]
        read_only_fields = ["id"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ["id", "sku", "color", "warranty", "price", "stock"]
        read_only_fields = ["id"]


class ProductReadSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "categories",
            "brand",
            "discount",
            "images",
            "variants",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "description",
            "categories",
            "brand",
            "discount",
            "is_active",
        ]


class ReviewReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "product",
            "rating",
            "comment",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["product", "rating", "comment"]


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    product_name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = Favorite
        fields = ["id", "user", "product", "product_name", "created_at"]
        read_only_fields = ["id", "user", "product_name", "created_at"]
