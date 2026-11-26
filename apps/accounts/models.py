import re

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models

from apps.core.models import TimeStampedModel


def normalize_phone(phone):
    """Normalize an Iranian mobile number to the local ``09XXXXXXXXX`` form."""
    if not phone:
        raise ValueError("Phone number cannot be empty.")

    phone = re.sub(r"[\s\-()]", "", str(phone))

    if phone.startswith("+98"):
        phone = "0" + phone[3:]
    elif phone.startswith("0098"):
        phone = "0" + phone[4:]
    elif phone.startswith("98") and len(phone) == 12:
        phone = "0" + phone[2:]

    if not re.fullmatch(r"09\d{9}", phone):
        raise ValueError("Enter a valid Iranian mobile number, e.g. 09181231234.")

    return phone


class CustomUserManager(BaseUserManager):
    """Manager for the project's email-based custom user model."""

    def create_user(self, email, password, phone, **extra_fields):
        if not email:
            raise ValueError("Email address cannot be empty.")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            phone=normalize_phone(phone),
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, phone, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")

        return self.create_user(email, password, phone, **extra_fields)


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

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.email


class Address(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
        db_index=False,
    )
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "addresses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"], name="addr_user_idx"),
            models.Index(fields=["is_default"], name="addr_default_idx"),
        ]

    def __str__(self):
        return f"{self.city} - {self.postal_code}"
