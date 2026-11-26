import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="categories__id")
    brand = django_filters.NumberFilter(field_name="brand__id")
    min_price = django_filters.NumberFilter(
        field_name="variants__price", lookup_expr="gte"
    )
    max_price = django_filters.NumberFilter(
        field_name="variants__price", lookup_expr="lte"
    )

    class Meta:
        model = Product
        fields = ["category", "brand", "min_price", "max_price"]
