from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.accounts.api.serializers import (
    AddressSerializer,
    ProfileSerializer,
    RegistrationSerializer,
)
from apps.accounts.models import Address
from apps.accounts.services import set_default_address


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class SetDefaultAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses=AddressSerializer)
    def post(self, request, pk):
        address = set_default_address(user=request.user, address_pk=pk)
        return Response(AddressSerializer(address).data)


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
