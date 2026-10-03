import pytest
from rest_framework.test import APIRequestFactory

from accounts.models import Profile, User
from blog.api.v1.serializers import (
    CategorySerializer,
    CommentSerializer,
    PostSerializer,
)
from blog.models import Category, Comment, Post


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@gmail.com",
        password="testpassword123",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@gmail.com",
        password="testpassword123",
    )


@pytest.fixture
def profile(user):
    return Profile.objects.get(user=user)


@pytest.fixture
def another_profile(another_user):
    return Profile.objects.get(user=another_user)


@pytest.fixture
def category(db):
    return Category.objects.create(name="Django")


@pytest.fixture
def another_category(db):
    return Category.objects.create(name="Python")


@pytest.fixture
def post(profile, category):
    return Post.objects.create(
        title="Test Post",
        content="This is test content",
        author=profile,
        category=category,
        status=True,
    )


@pytest.fixture
def another_post(another_profile, another_category):
    return Post.objects.create(
        title="Another Post",
        content="Another test content",
        author=another_profile,
        category=another_category,
        status=True,
    )


@pytest.fixture
def comment(profile, post):
    return Comment.objects.create(
        name="Test User",
        content="Test comment",
        author=profile,
        post=post,
        status=True,

    )


@pytest.fixture
def reply(another_profile, post, comment):
    return Comment.objects.create(
        name="Another User",
        content="Test reply",
        author=another_profile,
        post=post,
        parent=comment,
        status=True,

    )


@pytest.fixture
def api_request():
    factory = APIRequestFactory()
    request = factory.get("/blog/api/v1/post/")
    return request


@pytest.mark.django_db
class TestCategorySerializer:

    def test_category_serializer(self, category):
        serializer = CategorySerializer(category)

        assert serializer.data == {
            "id": category.id,
            "name": "Django",
        }


@pytest.mark.django_db
class TestPostSerializer:

    def test_post_serializer_list(self, post, api_request):
        api_request.parser_context = {"kwargs": {}}

        serializer = PostSerializer(
            post,
            context={"request": api_request},
        )

        data = serializer.data

        assert data["id"] == post.id
        assert data["title"] == "Test Post"
        assert data["author"] == post.author.id
        assert data["category"] == {
            "id": post.category.id,
            "name": "Django",
        }

        assert "content" not in data
        assert "comments" not in data

        assert "snippest" in data
        assert "post_url" in data

    def test_post_serializer_detail(self, post, api_request):
        api_request.parser_context = {
            "kwargs": {
                "pk": post.id,
            }
        }

        serializer = PostSerializer(
            post,
            context={"request": api_request},
        )

        data = serializer.data

        assert data["id"] == post.id
        assert data["title"] == "Test Post"
        assert data["content"] == "This is test content"

        assert data["category"] == {
            "id": post.category.id,
            "name": "Django",
        }

        assert "content" in data
        assert "comments" in data

        assert "snippest" not in data
        assert "post_url" not in data

    def test_post_serializer_category(self, post, api_request):
        api_request.parser_context = {"kwargs": {}}

        serializer = PostSerializer(
            post,
            context={"request": api_request},
        )

        assert serializer.data["category"] == {
            "id": post.category.id,
            "name": "Django",
        }

    def test_post_serializer_comments(self, post, comment, api_request):
        api_request.parser_context = {
            "kwargs": {
                "pk": post.id,
            }
        }

        serializer = PostSerializer(
            post,
            context={"request": api_request},
        )

        assert serializer.data["comments"] == [
            f"http://testserver/blog/api/v1/comment/{comment.id}/"
        ]

    def test_post_serializer_create(
        self,
        user,
        profile,
        category,
        api_request,
    ):
        api_request.user = user
        api_request.parser_context = {"kwargs": {}}

        data = {
            "title": "New Post",
            "content": "New post content",
            "category": category.id,
            "status": True,
        }

        serializer = PostSerializer(
            data=data,
            context={"request": api_request},
        )

        assert serializer.is_valid(), serializer.errors

        post = serializer.save()

        assert post.title == "New Post"
        assert post.content == "New post content"
        assert post.category == category
        assert post.author == profile


@pytest.mark.django_db
class TestCommentSerializer:

    def test_comment_serializer(self, comment, api_request):
        serializer = CommentSerializer(
            comment,
            context={"request": api_request},
        )

        data = serializer.data

        assert data["id"] == comment.id
        assert data["content"] == "Test comment"
        assert data["author"] == comment.author.id
        assert data["post"] == comment.post.id
        assert data["parent"] is None

        assert data["comment_parent_url"] is None

    def test_comment_serializer_parent(
        self,
        comment,
        reply,
        api_request,
    ):
        serializer = CommentSerializer(
            reply,
            context={"request": api_request},
        )

        data = serializer.data

        assert data["parent"] == comment.id

        assert (
            data["comment_parent_url"]
            == f"http://testserver/blog/api/v1/comment/{comment.id}/"
        )

    def test_comment_serializer_children(
        self,
        comment,
        reply,
        api_request,
    ):
        serializer = CommentSerializer(
            comment,
            context={"request": api_request},
        )

        data = serializer.data

        assert data["comment_children_url"] == [
            f"http://testserver/blog/api/v1/comment/{reply.id}/"
        ]

    def test_comment_serializer_create(
        self,
        user,
        profile,
        post,
        api_request,
    ):
        api_request.user = user

        data = {
            "content": "New comment",
            "post": post.id,
        }

        serializer = CommentSerializer(
            data=data,
            context={"request": api_request},
        )

        assert serializer.is_valid(), serializer.errors

        comment = serializer.save()

        assert comment.content == "New comment"
        assert comment.post == post
        assert comment.author == profile
        assert comment.name == profile.get_full_name()

    def test_comment_serializer_invalid_parent_post(
        self,
        post,
        another_post,
        comment,
        api_request,
    ):
        data = {
            "content": "Invalid reply",
            "post": another_post.id,
            "parent": comment.id,
        }

        serializer = CommentSerializer(
            data=data,
            context={"request": api_request},
        )

        assert serializer.is_valid() is False
        assert "parent" in serializer.errors
        assert (
            serializer.errors["parent"][0]
            == "Parent comment must belong to the same post."
        )

    def test_comment_serializer_read_only_fields(
        self,
        comment,
        api_request,
    ):
        data = {
            "name": "Changed Name",
            "author": comment.author.id,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "content": "Updated content",
            "post": comment.post.id,
        }

        serializer = CommentSerializer(
            comment,
            data=data,
            context={"request": api_request},
            partial=True,
        )

        assert serializer.is_valid(), serializer.errors

        updated_comment = serializer.save()

        assert updated_comment.name == comment.name
        assert updated_comment.author == comment.author
        assert updated_comment.content == "Updated content"
