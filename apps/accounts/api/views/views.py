from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..serializers.serializers import RegistrationSerializer


class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
