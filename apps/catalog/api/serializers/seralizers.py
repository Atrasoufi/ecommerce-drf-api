from rest_framework import serializers
from ...models import Category, Brands
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
