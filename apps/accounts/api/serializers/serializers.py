from rest_framework import serializers
from apps.accounts.models import Address
import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from ...models import UserModel

# Serializer پایه برای تعریف فیلدهای مشترک اطلاعات کاربر
class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        # مشخص کردن مدل مرتبط با Serializer
        model = UserModel

        # فیلدهای مشترک اطلاعات کاربر
        fields = ["id", "email", "phone"]

        # این فیلدها فقط خواندنی هستند و کلاینت نمی‌تواند آن‌ها را تغییر دهد
        read_only_fields = ["id"]


# Serializer مخصوص نمایش اطلاعات کاربر
class UserReadSerializer(UserBaseSerializer):
    # تمام فیلدها و تنظیمات کلاس پایه را به ارث می‌برد
    pass


# Serializer مخصوص ثبت‌نام کاربر
class RegistrationSerializer(serializers.ModelSerializer):

    # دریافت رمز عبور؛ این فیلد در خروجی نمایش داده نمی‌شود
    password = serializers.CharField(
        write_only=True,

        # فاصله‌های ابتدا و انتهای رمز عبور حذف نشوند
        trim_whitespace=False,

        # پیام‌های اختصاصی برای خطاهای ورودی
        error_messages={
            "required": "Password is required.",
            "blank": "Password cannot be empty.",
        },
    )

    # دریافت تأیید رمز عبور برای بررسی تطابق با رمز اصلی
    password1 = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        error_messages={
            "required": "Password confirmation is required.",
            "blank": "Password confirmation cannot be empty.",
        },
    )

    # دریافت شماره تلفن به‌صورت رشته
    phone = serializers.CharField(
        error_messages={
            "required": "Phone number is required.",
            "blank": "Phone number cannot be empty.",
        }
    )

    class Meta:
        # مدل مربوط به کاربران
        model = UserModel

        # فیلدهایی که هنگام ثبت‌نام از کلاینت دریافت می‌شوند
        fields = ["email", "phone", "password", "password1"]

    # اعتبارسنجی و یکسان‌سازی شماره تلفن
    def validate_phone(self, value):

        # حذف فاصله، خط تیره و پرانتز از شماره تلفن
        phone = re.sub(r"[\s\-()]", "", value)

        # تبدیل پیش‌شماره بین‌المللی ایران به فرمت داخلی
        if phone.startswith("+98"):
            phone = "0" + phone[3:]
        elif phone.startswith("0098"):
            phone = "0" + phone[4:]
        elif phone.startswith("98"):
            phone = "0" + phone[2:]

        # بررسی اینکه شماره با 09 شروع شده و ۱۱ رقم داشته باشد
        if not re.fullmatch(r"09\d{9}", phone):
            raise serializers.ValidationError(
                "Enter a valid Iranian mobile number, "
                "e.g. 09123456789."
            )

        # بررسی اینکه شماره قبلاً در دیتابیس ثبت نشده باشد
        if UserModel.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )

        # برگرداندن شماره تلفن نرمال‌شده
        return phone

    # اعتبارسنجی چند فیلد به‌صورت هم‌زمان
    def validate(self, attrs):

        # دریافت رمز عبور و تأیید آن از اطلاعات اعتبارسنجی‌شده
        password = attrs.get("password")
        password1 = attrs.get("password1")

        # بررسی تطابق رمز عبور با تأیید آن
        if password != password1:
            raise serializers.ValidationError({
                "password1": "Password confirmation does not match."
            })

        # بررسی رمز عبور بر اساس قوانین تنظیم‌شده در جنگو
        try:
            validate_password(password)

        # دریافت خطاهای اعتبارسنجی رمز عبور
        except ValidationError as exc:
            raise serializers.ValidationError({
                "password": list(exc.messages)
            })

        # برگرداندن اطلاعات در صورت موفقیت اعتبارسنجی
        return attrs

    # ساخت کاربر پس از موفقیت اعتبارسنجی‌ها
    def create(self, validated_data):

        # حذف تأیید رمز عبور؛ چون فیلد دیتابیس نیست
        validated_data.pop("password1")

        # ساخت کاربر با متد اختصاصی مدل کاربر
        # این متد باید رمز عبور را به‌صورت هش‌شده ذخیره کند
        return UserModel.objects.create_user(**validated_data)

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "id",
            "province",
            "city",
            "address",
            "postal_code",
            "is_default",
            "created_at",
        ]
        #این فیلد ها فقط قابل خواندن هستند و کاربر نمیتواند ان را تغییر دهد
        read_only_fields = ["id", "created_at"]