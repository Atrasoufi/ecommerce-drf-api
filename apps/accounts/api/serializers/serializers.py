from rest_framework import serializers
from apps.accounts.models import Address


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