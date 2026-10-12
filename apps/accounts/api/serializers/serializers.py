import re
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from ...models import UserModel


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
        # Remove spaces, hyphens and parentheses.
        phone = re.sub(r"[\s\-()]", "", value)

        # Normalize Iranian mobile number prefixes.
        if phone.startswith("+98"):
            phone = "0" + phone[3:]
        elif phone.startswith("0098"):
            phone = "0" + phone[4:]
        elif phone.startswith("98"):
            phone = "0" + phone[2:]

        # Validate the final Iranian mobile number.
        if not re.fullmatch(r"09\d{9}", phone):
            raise serializers.ValidationError(
                "Enter a valid Iranian mobile number, "
                "e.g. 09123456789."
            )

        if UserModel.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                "An account with this phone number already exists."
            )

        return phone

    def validate(self, attrs):
        password = attrs.get("password")
        password1 = attrs.get("password1")

        if password != password1:
            raise serializers.ValidationError({
                "password1": "Password confirmation does not match."
            })

        try:
            validate_password(password)
        except ValidationError as exc:
            raise serializers.ValidationError({
                "password": list(exc.messages)
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop("password1")
        return UserModel.objects.create_user(**validated_data)
