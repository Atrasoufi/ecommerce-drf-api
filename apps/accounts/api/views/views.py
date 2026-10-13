# from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.accounts.models import Address
from apps.accounts.api.serializers.serializers import AddressSerializer


# نمایش فهرست آدرس‌های کاربر و ایجاد آدرس جدید
class AddressListCreateView(generics.ListCreateAPIView):
    # مشخص کردن Serializer برای تبدیل داده‌های مدل به JSON و برعکس
    serializer_class = AddressSerializer

    # فقط کاربران واردشده اجازه دسترسی دارند
    permission_classes = [permissions.IsAuthenticated]

    # فقط آدرس‌های متعلق به کاربر فعلی نمایش داده می‌شوند
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    # هنگام ایجاد آدرس جدید، مالک آن را کاربر فعلی قرار می‌دهیم
    # بنابراین کاربر نمی‌تواند مالک آدرس را با ارسال اطلاعات دلخواه تعیین کند
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# مشاهده، ویرایش و حذف یک آدرس مشخص
class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Serializer مشخص کردن 
    serializer_class = AddressSerializer

    # فقط کاربران واردشده اجازه دسترسی دارند
    permission_classes = [permissions.IsAuthenticated]

    # جست‌وجوی آدرس فقط در میان آدرس‌های کاربر فعلی انجام می‌شود
    # اگر آدرس متعلق به شخص دیگری باشد، پیدا نمی‌شود و پاسخ 404 برمی‌گردد
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


# تعیین یک آدرس به‌عنوان آدرس پیش‌فرض کاربر
class SetDefaultAddressView(APIView):

    # فقط کاربران واردشده اجازه دسترسی دارند
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            # پیدا کردن آدرس با شناسه مشخص، فقط در میان آدرس‌های کاربر فعلی
            address = Address.objects.get(pk=pk, user=request.user)

        except Address.DoesNotExist:
            # اگر آدرس وجود نداشته باشد یا متعلق به کاربر دیگری باشد
            raise NotFound("Address not found.")

        # ابتدا تمام آدرس‌های کاربر فعلی را از حالت پیش‌ فرض خارج می‌کنیم
        Address.objects.filter(user=request.user).update(is_default=False)

        # آدرس انتخاب‌شده را به‌عنوان آدرس پیش‌ فرض مشخص می‌کنیم
        address.is_default = True

        #  فقط این فیلد ذخیره میشه در دیتابیس
        address.save(update_fields=["is_default"])

        #  اطلاعات آدرس انتخاب‌شده را در پاسخ برمی‌گردانیمAPI 
        return Response(AddressSerializer(address).data)
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..serializers.serializers import RegistrationSerializer


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
