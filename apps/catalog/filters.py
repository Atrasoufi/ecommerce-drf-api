import django_filters
from .models import Products

class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="categories__id", lookup_expr='iexact')
    brand = django_filters.NumberFilter(field_name="brands__id", lookup_expr='iexact')
    min_price = django_filters.NumberFilter(field_name="product_variants__price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="product_variants__price", lookup_expr='lte')
    
    class Meta:
        model = Products
        fields = ['category', 'brand', 'min_price', 'max_price']