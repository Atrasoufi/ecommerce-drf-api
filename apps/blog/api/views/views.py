from django.shortcuts import get_object_or_404

from rest_framework import request, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response

from ...models import Comment, Post
from ..serializers.serializers import (
    CommentReadSerializer,
    CommentWriteSerializer,
)
from .permissions import IsCommentOwnerOrStaff


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related(
        "post",
        "user",
    )

    def get_queryset(self):
        queryset = super().get_queryset()

        # فهرست عمومی فقط کامنت‌های تأییدشده را نمایش می‌دهد.
        if self.action == "list":
            queryset = queryset.filter(is_approved=True)

            post_id = self.request.query_params.get("post")

            if post_id:
                queryset = queryset.filter(post_id=post_id)

            return queryset

        # جزئیات کامنت برای کاربران عادی در دسترس نیست.
        if self.action == "retrieve":
            if self.request.user.is_staff:
                return queryset

            if self.request.user.is_authenticated:
                return queryset.filter(
                    user=self.request.user,
                    is_approved=True,
                )

            return queryset.filter(is_approved=True)

        # staff می‌تواند تمام کامنت‌ها را مدیریت کند.
        if self.action in ["approve", "reject"]:
            return queryset

        # نویسنده فقط کامنت خودش را حذف می‌کند.
        if self.action == "destroy":
            if self.request.user.is_staff:
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
                IsCommentOwnerOrStaff,
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

    # def destroy(self, request, *args, **kwargs):
    #     comment = self.get_object()
    #     self.check_object_permissions(request, comment)
    #     comment.delete()

    #     return Response(
    #         status=status.HTTP_204_NO_CONTENT,
    #     )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
