from rest_framework import serializers

from apps.blog.models import Comment, Post


class PostReadSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "author",
            "is_published",
            "published_at",
            "thumbnail",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["title", "content", "is_published", "thumbnail"]


class CommentReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

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
        read_only_fields = fields


class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["post", "content"]
