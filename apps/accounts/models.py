from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
import re


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
    def create_user(self, email, password, **kwargs):
        if not email:
            return ValueError("email can not be empty...!")
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_active", True)
        if kwargs.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if kwargs.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if kwargs.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        return self.create_user(email, password, **kwargs)



class UserModel(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=11, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    objects = CustomeManager()

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email




# Create your models here.