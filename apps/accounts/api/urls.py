from django.urls import path
from .views.views import RegistrationAPIView
from apps.accounts.api.views.views import ProfileView

from apps.accounts.api.views.views import (
    AddressListCreateView,
    AddressDetailView,
    SetDefaultAddressView,
)


# API تعریف مسیرهای مربوط به  
urlpatterns = [
    # POST ایجاد آدرس جدید با 
    # GET نمایش فهرست ادرس ها با 
    path(
        "addresses/",
        AddressListCreateView.as_view(),
        name="address-list-create",
    ),

    # PUT ویرایش کامل با 
    # PATCH ویرایش بخشی از اطلاعات  
    # DELETحذف کردن با 
    path(
        "addresses/<int:pk>/",
        AddressDetailView.as_view(),
        name="address-detail",
    ),

    # تعیین آدرس مشخص‌ شده به‌عنوان آدرس پیش‌ فرض  
    path(
        "addresses/<int:pk>/set-default/",
        SetDefaultAddressView.as_view(),
        name="address-set-default",
    ),
    
    path(
        "register/",
        RegistrationAPIView.as_view(),
        name="register",
    ),
  
    path("profile/", ProfileView.as_view(), name="profile"),
]


