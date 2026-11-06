from django.utils import timezone
from rest_framework import serializers
from apps.blog.models import Post, Comment


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'slug',
            'content',
            'author',
            'is_published',
            'published_at',
            'thumbnail',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['published_at', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # Automatically set published_at timestamp when a post is published for the first time
        is_published_new = validated_data.get(
            'is_published', instance.is_published
        )
        if is_published_new and not instance.is_published:
            if not instance.published_at:
                validated_data['published_at'] = timezone.now()

        return super().update(instance, validated_data)


class CommentReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post',
            'user',
            'content',
            'is_approved',
            'created_at',
        ]


class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'post',
            'content',
        ]