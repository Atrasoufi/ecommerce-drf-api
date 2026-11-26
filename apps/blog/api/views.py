from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from apps.blog.api.serializers import (
    CommentReadSerializer,
    CommentWriteSerializer,
    PostReadSerializer,
    PostWriteSerializer,
)
from apps.blog.services import (
    create_comment,
    create_post,
    get_comment_queryset,
    get_post_queryset,
    set_comment_approval,
    update_post,
)
from apps.core.permissions import (
    IsAuthorOrStaffOrReadOnly,
    IsOwnerOrStaffOrReadOnly,
)


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostWriteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "is_published"]

    def get_queryset(self):
        return get_post_queryset(user=self.request.user)

    def get_serializer_class(self):
        if self.action in {"list", "retrieve"}:
            return PostReadSerializer
        return PostWriteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = create_post(
            author=request.user,
            validated_data=serializer.validated_data,
        )
        output = PostReadSerializer(
            post, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(output.data)
        return Response(output.data, status.HTTP_201_CREATED, headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        post = update_post(
            instance=instance,
            validated_data=serializer.validated_data,
        )
        return Response(
            PostReadSerializer(
                post, context=self.get_serializer_context()
            ).data
        )


class CommentViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = get_comment_queryset()
        user = self.request.user

        if self.action == "list":
            queryset = queryset.filter(is_approved=True)
            post_id = self.request.query_params.get("post")
            if post_id:
                queryset = queryset.filter(post_id=post_id)
            return queryset

        if self.action == "retrieve":
            if user.is_authenticated and user.is_staff:
                return queryset
            if user.is_authenticated:
                return queryset.filter(Q(is_approved=True) | Q(user=user))
            return queryset.filter(is_approved=True)

        if self.action in {"approve", "reject"}:
            return queryset

        if self.action == "destroy":
            if user.is_authenticated and user.is_staff:
                return queryset
            return queryset.filter(user=user)

        return queryset.none()

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [AllowAny]
        elif self.action == "create":
            permission_classes = [IsAuthenticated]
        elif self.action in {"approve", "reject"}:
            permission_classes = [IsAdminUser]
        elif self.action == "destroy":
            permission_classes = [IsAuthenticated, IsOwnerOrStaffOrReadOnly]
        else:
            permission_classes = [IsAdminUser]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentWriteSerializer
        return CommentReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = create_comment(
            user=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(
            CommentReadSerializer(
                comment, context=self.get_serializer_context()
            ).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        comment = set_comment_approval(comment_pk=pk, is_approved=True)
        return Response(
            CommentReadSerializer(
                comment, context=self.get_serializer_context()
            ).data
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        comment = set_comment_approval(comment_pk=pk, is_approved=False)
        return Response(
            CommentReadSerializer(
                comment, context=self.get_serializer_context()
            ).data
        )
