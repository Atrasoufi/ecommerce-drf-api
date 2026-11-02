from rest_framework import serializers

from ...models import Comment


# Serializer پایه کامنت
class CommentBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "user",
            "content",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "is_approved",
            "created_at",
            "updated_at",
        ]


# Serializer مخصوص نمایش کامنت
class CommentReadSerializer(CommentBaseSerializer):
    class Meta(CommentBaseSerializer.Meta):
        fields = CommentBaseSerializer.Meta.fields


# Serializer مخصوص ایجاد و ویرایش کامنت
class CommentWriteSerializer(CommentBaseSerializer):
    class Meta(CommentBaseSerializer.Meta):
        fields = [
            "post",
            "content",
        ]

    # بررسی خالی نبودن متن کامنت
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "متن کامنت نمی‌تواند خالی باشد."
            )

        return value