
from django.contrib import admin
from .models import UserModel, Address


admin.site.register(UserModel)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id","user","province","city","postal_code","is_default","created_at",)
    list_filter = ("province","city","is_default",)
    search_fields = ("province","city","postal_code","address","user__email",)
    readonly_fields = ("created_at",)



