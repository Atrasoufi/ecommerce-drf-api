from rest_framework import serializers
from apps.catalog.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    # برای اینکه به جای آیدی کاربر، اسمش نمایش داده بشه
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 
            'user', 
            'product', 
            'rating', 
            'comment', 
            'is_approved', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['is_approved', 'created_at', 'updated_at']