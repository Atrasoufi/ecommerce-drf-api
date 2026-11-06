from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
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

from apps.blog.models import Comment, Post
from ..serializers.serializers import (
    CommentReadSerializer,
    CommentWriteSerializer,
    PostSerializer,
)
from apps.blog.permissions import IsAuthorOrStaffOrReadOnly, IsCommentOwnerOrStaff


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrStaffOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'is_published']

    def get_queryset(self):
        user = self.request.user
        
        # Staff and admins can view all posts (published and drafts)
        if user.is_authenticated and user.is_staff:
            return Post.objects.all().order_by('-created_at')

        # Regular users and guests only see published posts
        return Post.objects.filter(is_published=True).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically generate a unique slug from the post title
        title = serializer.validated_data.get('title')
        base_slug = slugify(title)
        slug = base_slug
        counter = 1

        # Ensure slug uniqueness in the database
        while Post.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        # Set publishing timestamp if the post is created as published
        is_published = serializer.validated_data.get('is_published', False)
        published_at = (
            timezone.now()
            if is_published
            else None
        )

        serializer.save(
            author=self.request.user,
            slug=slug,
            published_at=published_at,
        )


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "post",
        "user",
    )

    def get_queryset(self):
        queryset = super().get_queryset()

        # Public list endpoint only displays approved comments
        if self.action == "list":
            queryset = queryset.filter(is_approved=True)

            post_id = self.request.query_params.get("post")

            if post_id:
                queryset = queryset.filter(post_id=post_id)

            return queryset

        # Detail view permissions based on user role and comment status
        if self.action == "retrieve":
            if self.request.user.is_authenticated and self.request.user.is_staff:
                return queryset

            if self.request.user.is_authenticated:
                return queryset.filter(
                    models.Q(is_approved=True) | models.Q(user=self.request.user)
                )

            return queryset.filter(is_approved=True)

        # Staff can manage approval actions for all comments
        if self.action in ["approve", "reject"]:
            return queryset

        # Authors or staff can delete comments
        if self.action == "destroy":
            if self.request.user.is_authenticated and self.request.user.is_staff:
                return queryset

            return queryset.filter(user=self.request.user)

        return queryset.none()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]

        elif self.action == "create":
            permission_classes = [IsAuthenticated]

        elif self.action in ["approve", "reject"]:
            permission_classes = [IsAdminUser]

        elif self.action == "destroy":
            permission_classes = [
                IsAuthenticated,
            ]

        else:
            permission_classes = [IsAdminUser]

        return [
            permission()
            for permission in permission_classes
        ]

    def get_serializer_class(self):
        if self.action == "create":
            return CommentWriteSerializer

        return CommentReadSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save(
            user=request.user,
            is_approved=False,
        )

        output = CommentReadSerializer(
            comment,
            context=self.get_serializer_context(),
        )

        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def approve(self, request, pk=None):
        comment = get_object_or_404(
            Comment.objects.select_related("post", "user"),
            pk=pk,
        )

        comment.is_approved = True
        comment.save(update_fields=["is_approved"])

        return Response(
            CommentReadSerializer(
                comment,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[IsAdminUser],
    )
    def reject(self, request, pk=None):
        comment = get_object_or_404(
            Comment.objects.select_related("post", "user"),
            pk=pk,
        )

        comment.is_approved = False
        comment.save(update_fields=["is_approved"])

        return Response(
            CommentReadSerializer(
                comment,
                context=self.get_serializer_context(),
            ).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)