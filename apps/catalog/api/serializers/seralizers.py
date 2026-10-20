from rest_framework import serializers
from ...models import Category, Brands, Products, Product_Images, Product_Variants
# =========================
# Serializer های دسته‌بندی
# =========================

# فیلدهای مشترک دسته‌بندی
class CategoryBaseSerializer(serializers.ModelSerializer):
    class Meta:
        # مدل مرتبط با این Serializer
        model = Category
        # فیلدهای مشترک دسته‌بندی
        fields = ["id", "name", "slug", "description"]
        # شناسه و اسلاگ به‌صورت خودکار مدیریت می‌شوند
        read_only_fields = ["id", "slug"]


# Serializer مخصوص نمایش دسته‌بندی
class CategoryReadSerializer(CategoryBaseSerializer):
    # فیلدهای کلاس پایه را به ارث می‌برد
    pass


# Serializer مخصوص ایجاد و ویرایش دسته‌بندی
class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        # مدل دسته‌بندی
        model = Category

        # فقط فیلدهایی که کلاینت اجازه ارسال آن‌ها را دارد
        fields = ["name", "slug","description"]


# =========================
# Serializer های برند
# =========================

# فیلدهای مشترک برند
class BrandsBaseSerializer(serializers.ModelSerializer):
    class Meta:
        # مدل مرتبط با برند
        model = Brands
        # فیلدهای مشترک برند
        fields = ["id", "name", "slug"]
        # شناسه و اسلاگ فقط خواندنی هستند
        read_only_fields = ["id", "slug"]

# Serializer مخصوص نمایش برند
class BrandsReadSerializer(BrandsBaseSerializer):
    # فیلدهای کلاس پایه را به ارث می‌برد
    pass

# Serializer مخصوص ایجاد و ویرایش برند
class BrandsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        # مدل برند
        model = Brands
        # فیلدهای مجاز برای دریافت از کلاینت
        fields = ["name","slug"]
        
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Images
        fields = ["id", "image", "is_primary"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product_Variants
        fields = [
            "id",
            "sku",
            "color",
            "warranty",
            "price",
            "stock",
        ]


class ProductsListSerializer(serializers.ModelSerializer):
    categories = CategoryReadSerializer(many=True, read_only=True)
    brand = BrandsReadSerializer(read_only=True)

    images = ProductImageSerializer(
        source="product_images_set",
        many=True,
        read_only=True,
    )

    variants = ProductVariantSerializer(
        source="product_variants_set",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Products
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "categories",
            "brand",
            "images",
            "variants",
            "created_at",
        ]


class ProductsDetailSerializer(ProductsListSerializer):
    class Meta(ProductsListSerializer.Meta):
        fields = ProductsListSerializer.Meta.fields + [
            "updated_at",
        ]
