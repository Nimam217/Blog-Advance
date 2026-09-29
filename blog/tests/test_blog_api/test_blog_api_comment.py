import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Profile, User
from blog.models import Category, Comment, Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def my_user(db):
    return User.objects.create_user(
        email="commentuser@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="anothercomment@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def my_profile(my_user):
    return Profile.objects.get(user=my_user)


@pytest.fixture
def another_profile(another_user):
    return Profile.objects.get(user=another_user)


@pytest.fixture
def my_category(db):
    return Category.objects.create(
        name="test category",
    )


@pytest.fixture
def another_category(db):
    return Category.objects.create(
        name="another category",
    )


@pytest.fixture
def my_post(my_profile, my_category):
    return Post.objects.create(
        title="test post",
        content="test content",
        author=my_profile,
        category=my_category,
        status=True,
    )


@pytest.fixture
def another_post(another_profile, another_category):
    return Post.objects.create(
        title="another post",
        content="another content",
        author=another_profile,
        category=another_category,
        status=True,
    )


@pytest.fixture
def my_comment(my_profile, my_post):
    return Comment.objects.create(
        name=my_profile.get_full_name(),
        content="test comment",
        author=my_profile,
        post=my_post,
    )


@pytest.fixture
def another_comment(another_profile, my_post):
    return Comment.objects.create(
        name=another_profile.get_full_name(),
        content="another comment",
        author=another_profile,
        post=my_post,
    )


@pytest.fixture
def reply_comment(another_profile, my_post, my_comment):
    return Comment.objects.create(
        name=another_profile.get_full_name(),
        content="test reply",
        author=another_profile,
        post=my_post,
        parent=my_comment,
    )


@pytest.mark.django_db
class TestCommentAPI:

    # =========================================================
    # LIST
    # =========================================================

    def test_comment_list_authenticated(
        self,
        api_client,
        my_user,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(url)

        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == my_comment.id

    def test_comment_list_unauthenticated(
        self,
        api_client,
    ):
        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(url)

        assert response.status_code == 401

    # =========================================================
    # DETAIL
    # =========================================================

    def test_comment_detail_authenticated(
        self,
        api_client,
        my_user,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == my_comment.id
        assert response.data["content"] == "test comment"

    def test_comment_detail_unauthenticated(
        self,
        api_client,
        my_comment,
    ):
        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 401

    def test_comment_detail_not_found(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.get(url)

        assert response.status_code == 404

    # =========================================================
    # CREATE
    # =========================================================

    def test_comment_create_authenticated(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        data = {
            "content": "new comment",
            "post": my_post.pk,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 201

        comment = Comment.objects.get(content="new comment")

        assert comment.post == my_post
        assert comment.author == Profile.objects.get(user=my_user)

    def test_comment_create_unauthenticated(
        self,
        api_client,
        my_post,
    ):
        url = reverse("blog:api_v1:comment-api-list")

        data = {
            "content": "new comment",
            "post": my_post.pk,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 401

        assert not Comment.objects.filter(content="new comment").exists()

    def test_comment_create_invalid_data(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.post(
            url,
            {},
            format="json",
        )

        assert response.status_code == 400

    # =========================================================
    # AUTHOR / NAME
    # =========================================================

    def test_comment_author_is_set_automatically(
        self,
        api_client,
        my_user,
        my_profile,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.post(
            url,
            {
                "content": "author test",
                "post": my_post.pk,
            },
            format="json",
        )

        assert response.status_code == 201

        comment = Comment.objects.get(content="author test")

        assert comment.author == my_profile

    def test_comment_name_is_set_automatically(
        self,
        api_client,
        my_user,
        my_profile,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.post(
            url,
            {
                "content": "name test",
                "post": my_post.pk,
            },
            format="json",
        )

        assert response.status_code == 201

        comment = Comment.objects.get(content="name test")

        assert comment.name == my_profile.get_full_name()

    # =========================================================
    # PARENT / REPLY
    # =========================================================

    def test_create_reply_comment(
        self,
        api_client,
        my_user,
        my_post,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.post(
            url,
            {
                "content": "this is a reply",
                "post": my_post.pk,
                "parent": my_comment.pk,
            },
            format="json",
        )

        assert response.status_code == 201

        reply = Comment.objects.get(content="this is a reply")

        assert reply.parent == my_comment
        assert reply.post == my_post

    def test_parent_must_belong_to_same_post(
        self,
        api_client,
        my_user,
        my_post,
        another_post,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.post(
            url,
            {
                "content": "invalid reply",
                "post": another_post.pk,
                "parent": my_comment.pk,
            },
            format="json",
        )

        assert response.status_code == 400

        assert not Comment.objects.filter(content="invalid reply").exists()

    # =========================================================
    # UPDATE
    # =========================================================

    def test_comment_update_owner(
        self,
        api_client,
        my_user,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.patch(
            url,
            {
                "content": "updated comment",
            },
            format="json",
        )

        assert response.status_code == 200

        my_comment.refresh_from_db()

        assert my_comment.content == "updated comment"

    def test_comment_update_not_owner(
        self,
        api_client,
        another_user,
        my_comment,
    ):
        api_client.force_authenticate(user=another_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.patch(
            url,
            {
                "content": "hacked comment",
            },
            format="json",
        )

        assert response.status_code == 403

        my_comment.refresh_from_db()

        assert my_comment.content == "test comment"

    def test_comment_update_unauthenticated(
        self,
        api_client,
        my_comment,
    ):
        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.patch(
            url,
            {
                "content": "updated",
            },
            format="json",
        )

        assert response.status_code == 401

    # =========================================================
    # DELETE
    # =========================================================

    def test_comment_delete_owner(
        self,
        api_client,
        my_user,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 204

        assert not Comment.objects.filter(pk=my_comment.pk).exists()

    def test_comment_delete_not_owner(
        self,
        api_client,
        another_user,
        my_comment,
    ):
        api_client.force_authenticate(user=another_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 403

        assert Comment.objects.filter(pk=my_comment.pk).exists()

    def test_comment_delete_unauthenticated(
        self,
        api_client,
        my_comment,
    ):
        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 401

        assert Comment.objects.filter(pk=my_comment.pk).exists()

    # =========================================================
    # FILTER
    # =========================================================

    def test_filter_by_post(
        self,
        api_client,
        my_user,
        my_comment,
        another_post,
        another_profile,
    ):
        Comment.objects.create(
            name=another_profile.get_full_name(),
            content="another post comment",
            author=another_profile,
            post=another_post,
        )

        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"post": my_comment.post.pk},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["id"] == my_comment.pk

    def test_filter_by_author(
        self,
        api_client,
        my_user,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"author": my_comment.author.pk},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["author"] == my_comment.author.pk

    def test_filter_by_parent(
        self,
        api_client,
        my_user,
        my_comment,
        reply_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"parent": my_comment.pk},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["id"] == reply_comment.pk
        assert data[0]["parent"] == my_comment.pk

    # =========================================================
    # SEARCH
    # =========================================================

    def test_search_by_content(
        self,
        api_client,
        my_user,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"search": "test comment"},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["id"] == my_comment.pk

    def test_search_by_name(
        self,
        api_client,
        my_user,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"search": my_comment.name},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) >= 1

    # =========================================================
    # ORDERING
    # =========================================================

    def test_ordering_created_at(
        self,
        api_client,
        my_user,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"ordering": "created_at"},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 2

        dates = [comment["created_at"] for comment in data]

        assert dates == sorted(dates)

    def test_ordering_updated_at(
        self,
        api_client,
        my_user,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:comment-api-list")

        response = api_client.get(
            url,
            {"ordering": "updated_at"},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 2

        dates = [comment["updated_at"] for comment in data]

        assert dates == sorted(dates)

    # =========================================================
    # SERIALIZER REPRESENTATION
    # =========================================================

    def test_comment_parent_url_for_root_comment(
        self,
        api_client,
        my_user,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["comment_parent_url"] is None

    def test_comment_parent_url_for_reply(
        self,
        api_client,
        my_user,
        reply_comment,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": reply_comment.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        assert response.data["comment_parent_url"] == (
            f"http://testserver/blog/api/v1/comment/{my_comment.pk}/"
        )

    def test_comment_children_url(
        self,
        api_client,
        my_user,
        my_comment,
        reply_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:comment-api-detail",
            kwargs={"pk": my_comment.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        children = response.data["comment_children_url"]

        assert len(children) == 1

        assert children[0] == (
            f"http://testserver/blog/api/v1/comment/{reply_comment.pk}/"
        )
