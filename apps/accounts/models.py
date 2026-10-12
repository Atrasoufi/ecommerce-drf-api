from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import re
from django.conf import settings



def normalize_phone(phone):
    if not phone:
        raise ValueError("Phone number cannot be empty!")

    # حذف فاصله، خط تیره و سایر کاراکترهای اضافی
    phone = re.sub(r"[\s\-()]", "", phone)

    # تبدیل پیش‌شماره ایران به فرمت داخلی
    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("0098"):
        phone = "0" + phone[4:]
    elif phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]

    # اعتبارسنجی شماره موبایل ایران
    if not re.fullmatch(r"09\d{9}", phone):
        raise ValueError(
            "Enter a valid mobile number, e.g. 09181231234"
        )

    return phone


class CustomeManager(BaseUserManager):
    def create_user(self, email, password,phone, **kwargs):
        if not email:
            return ValueError("email can not be empty...!")
        email = self.normalize_email(email)
        phone = normalize_phone(phone)
        user = self.model(email=email,phone=phone, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, phone, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if kwargs.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        return self.create_user(email, password, phone, **kwargs)



class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone"]

    objects = CustomeManager()

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email



class Address(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="addresses",db_index=False)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"
        indexes = [
            models.Index(fields=["user"], name="addr_user_idx"),
            models.Index(fields=["is_default"], name="addr_default_idx"),
        ]

    def __str__(self):
        return f"{self.city} - {self.postal_code}"

