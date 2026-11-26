"""Rename catalog models to singular PascalCase names.

This migration depends on the initial carts/orders migrations so their foreign
keys are already present in the migration state and are updated by
``RenameModel`` automatically.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0007_alter_review_options_alter_favorite_unique_together_and_more"),
        ("carts", "0001_initial"),
        ("orders", "0002_remove_orderitem_orderitem_order_idx_and_more"),
    ]

    operations = [
        migrations.RenameModel(old_name="Discount_Type", new_name="DiscountType"),
        migrations.RenameModel(old_name="Brands", new_name="Brand"),
        migrations.RenameModel(old_name="Products", new_name="Product"),
        migrations.RenameModel(old_name="Product_Images", new_name="ProductImage"),
        migrations.RenameModel(old_name="Product_Variants", new_name="ProductVariant"),
    ]
