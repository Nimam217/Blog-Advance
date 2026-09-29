from rest_framework import serializers

from blog.models import Post, Category, Comment
from accounts.models import Profile


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class CommentSerializer(serializers.ModelSerializer):
    comment_children_url = serializers.SerializerMethodField()
    comment_parent_url = serializers.SerializerMethodField()
    post = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.filter(status=True)
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "name",
            "content",
            "author",
            "post",
            "parent",
            "created_at",
            "updated_at",
            "comment_children_url",
            "comment_parent_url",
        ]

        read_only_fields = [
            "id",
            "name",
            "author",
            "created_at",
            "updated_at",
            "comment_parent_url",
        ]

    def validate(self, attrs):
        post = attrs.get("post")
        parent = attrs.get("parent")

        if parent and parent.post_id != post.id:
            raise serializers.ValidationError(
                {"parent": "Parent comment must belong to the same post."}
            )

        return attrs

    def create(self, validated_data):
        profile = Profile.objects.get(user=self.context["request"].user)

        validated_data["author"] = profile
        validated_data["name"] = profile.get_full_name()

        return super().create(validated_data)

    def get_comment_children_url(self, obj):
        request = self.context.get("request")
        return [
            (request.build_absolute_uri(f"/blog/api/v1/comment/{comment.id}/"))
            for comment in obj.replies.all()
        ]

    def get_comment_parent_url(self, obj):
        request = self.context.get("request")
        if not obj.parent_id:
            return None
        return request.build_absolute_uri(
            f"/blog/api/v1/comment/{obj.parent_id}/"
        )


class PostSerializer(serializers.ModelSerializer):
    post_url = serializers.SerializerMethodField()
    snippest = serializers.ReadOnlyField(source="get_snippets")
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "post_url",
            "image",
            "title",
            "content",
            "snippest",
            "author",
            "category",
            "status",
            "created_at",
            "comments",
        ]
        read_only_fields = ["author"]

    def get_post_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(obj.id)

    def get_comments(self, obj):
        request = self.context.get("request")

        return [
            request.build_absolute_uri(f"/blog/api/v1/comment/{comment.id}/")
            for comment in obj.comments.all()
        ]

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)

        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippest", None)
            rep.pop("post_url", None)
        else:
            rep.pop("content", None)
            rep.pop("comments", None)

        rep["category"] = CategorySerializer(instance.category).data

        return rep

    def create(self, validated_data):
        validated_data["author"] = Profile.objects.get(
            user__id=self.context["request"].user.id
        )

        return super().create(validated_data)
