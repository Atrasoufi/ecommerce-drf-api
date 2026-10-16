
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.accounts.api.serializers.serializers import ProfileSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
