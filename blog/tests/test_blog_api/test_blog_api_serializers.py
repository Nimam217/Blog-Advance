'''import pytest

from rest_framework.test import APIRequestFactory

from accounts.models import Profile, User
from blog.models import Category, Post
from blog.api.v1.serializers import PostSerializer


@pytest.fixture
def serializer_user(db):
    return User.objects.create_user(
        email="serializer@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def serializer_profile(serializer_user):
    return Profile.objects.get(user=serializer_user)


@pytest.fixture
def serializer_category(db):
    return Category.objects.create(
        name="serializer category",
    )


@pytest.fixture
def serializer_post(
    serializer_profile,
    serializer_category,
):
    return Post.objects.create(
        title="serializer post",
        content="serializer content",
        author=serializer_profile,
        category=serializer_category,
        status=True,
    )


@pytest.fixture
def request_factory():
    return APIRequestFactory()


@pytest.mark.django_db
class TestPostSerializer:

    # --------------------------------
    # Expected fields
    # --------------------------------

    def test_serializer_contains_expected_fields(
        self,
        request_factory,
        serializer_post,
    ):
        request = request_factory.get("/api/v1/posts/")

        request.parser_context = {"kwargs": {}}

        serializer = PostSerializer(
            serializer_post,
            context={
                "request": request,
            },
        )

        data = serializer.data

        assert "id" in data
        assert "post_url" in data
        assert "image" in data
        assert "title" in data
        assert "snippest" in data
        assert "author" in data
        assert "category" in data
        assert "status" in data
        assert "created_at" in data

    # --------------------------------
    # List representation
    # --------------------------------

    def test_list_representation(
        self,
        request_factory,
        serializer_post,
    ):
        request = request_factory.get("/api/v1/posts/")

        request.parser_context = {"kwargs": {}}

        serializer = PostSerializer(
            serializer_post,
            context={
                "request": request,
            },
        )

        data = serializer.data

        assert "content" not in data
        assert "snippest" in data
        assert "post_url" in data

    # --------------------------------
    # Detail representation
    # --------------------------------

    def test_detail_representation(
        self,
        request_factory,
        serializer_post,
    ):
        request = request_factory.get(f"/api/v1/posts/{serializer_post.pk}/")

        request.parser_context = {
            "kwargs": {
                "pk": serializer_post.pk,
            }
        }

        serializer = PostSerializer(
            serializer_post,
            context={
                "request": request,
            },
        )

        data = serializer.data

        assert "content" in data
        assert "snippest" not in data
        assert "post_url" not in data

    # --------------------------------
    # Nested category
    # --------------------------------

    def test_category_is_nested(
        self,
        request_factory,
        serializer_post,
    ):
        request = request_factory.get(f"/api/v1/posts/{serializer_post.pk}/")

        request.parser_context = {
            "kwargs": {
                "pk": serializer_post.pk,
            }
        }

        serializer = PostSerializer(
            serializer_post,
            context={
                "request": request,
            },
        )

        data = serializer.data

        assert isinstance(
            data["category"],
            dict,
        )

        assert data["category"]["id"] == (serializer_post.category.pk)

        assert data["category"]["name"] == (serializer_post.category.name)

    # --------------------------------
    # Author is read only
    # --------------------------------

    def test_author_is_read_only(
        self,
        serializer_post,
    ):
        serializer = PostSerializer(serializer_post)

        assert "author" in serializer.fields

        assert serializer.fields["author"].read_only is True

    # --------------------------------
    # Create
    # --------------------------------

    def test_create_sets_author_automatically(
        self,
        request_factory,
        serializer_user,
        serializer_category,
    ):
        request = request_factory.post("/api/v1/posts/")

        request.user = serializer_user

        request.parser_context = {"kwargs": {}}

        data = {
            "title": "created post",
            "content": "created content",
            "category": serializer_category.pk,
            "status": True,
        }

        serializer = PostSerializer(
            data=data,
            context={
                "request": request,
            },
        )

        assert serializer.is_valid()

        post = serializer.save()

        profile = Profile.objects.get(user=serializer_user)

        assert post.author == profile

    # --------------------------------
    # Invalid data
    # --------------------------------

    def test_serializer_invalid_without_title(
        self,
        request_factory,
        serializer_user,
    ):
        request = request_factory.post("/api/v1/posts/")

        request.user = serializer_user

        request.parser_context = {"kwargs": {}}

        data = {
            "content": "content without title",
            "status": True,
        }

        serializer = PostSerializer(
            data=data,
            context={
                "request": request,
            },
        )

        assert serializer.is_valid() is False

        assert "title" in serializer.errors
'''