from rest_framework import serializers

from blog.models import Post, Category
from accounts.models import Profile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
        ]


class PostSerializer(serializers.ModelSerializer):
    post_url = serializers.SerializerMethodField()
    snippest = serializers.ReadOnlyField(source="get_snippets")

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
        ]
        read_only_fields = ["author"]

    def get_post_url(self, obj):
        request = self.context.get("request")

        return request.build_absolute_uri(obj.id)

    def to_representation(self, instance):
        request = self.context.get("request")
        rep = super().to_representation(instance)

        if request.parser_context.get("kwargs").get("pk"):
            rep.pop("snippest", None)
            rep.pop("post_url", None)

        else:
            rep.pop("content", None)
        rep["category"] = CategorySerializer(instance.category).data
        return rep

    def create(self, validated_data):

        validated_data["author"] = Profile.objects.get(
            user__id=self.context["request"].user.id
        )
        return super().create(validated_data)
