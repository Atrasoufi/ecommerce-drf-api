from rest_framework import serializers
from apps.catalog.models import Favorite

class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    # برای اینکه به جای آیدی محصول، اسمش نمایش داده بشه
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = Favorite
        fields = [
            'id', 
            'user', 
            'product', 
            'product_name', 
            'created_at'
        ]
        read_only_fields = ['created_at']