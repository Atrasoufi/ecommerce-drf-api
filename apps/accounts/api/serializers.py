from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.accounts.models import Address, UserModel, normalize_phone


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "email", "phone", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        error_messages={
            "required": "Password is required.",
            "blank": "Password cannot be empty.",
        },
    )
    password1 = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        error_messages={
            "required": "Password confirmation is required.",
            "blank": "Password confirmation cannot be empty.",
        },
    )
    phone = serializers.CharField(
        error_messages={
            "required": "Phone number is required.",
            "blank": "Phone number cannot be empty.",
        }
    )

    class Meta:
        model = UserModel
        fields = ["email", "phone", "password", "password1"]

    def validate_phone(self, value):
        try:
            phone = normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

        if UserModel.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )
        return phone

    def validate(self, attrs):
        if attrs["password"] != attrs["password1"]:
            raise serializers.ValidationError(
                {"password1": "Password confirmation does not match."}
            )

        try:
            validate_password(attrs["password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                {"password": list(exc.messages)}
            ) from exc

        return attrs

    def create(self, validated_data):
        validated_data.pop("password1")
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
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
