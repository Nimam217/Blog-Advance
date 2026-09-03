import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Profile, User
from blog.models import Category, Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def my_user(db):
    return User.objects.create_user(
        email="testfixture@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def another_user(db):
    return User.objects.create_user(
        email="another@gmail.com",
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


@pytest.mark.django_db
class TestPostAPI:

    # -------------------------
    # LIST
    # -------------------------

    def test_post_list_authenticated(self, api_client, my_user):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

    def test_post_list_unauthenticated(self, api_client):
        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 401

    def test_post_list_only_active_posts(
        self,
        api_client,
        my_user,
        my_profile,
        my_category,
    ):
        Post.objects.create(
            title="active post",
            content="active content",
            author=my_profile,
            category=my_category,
            status=True,
        )

        Post.objects.create(
            title="inactive post",
            content="inactive content",
            author=my_profile,
            category=my_category,
            status=False,
        )

        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        data = response.data["results"]

        titles = [post["title"] for post in data]

        assert "active post" in titles
        assert "inactive post" not in titles

    # -------------------------
    # RETRIEVE
    # -------------------------

    def test_post_detail_authenticated(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

    def test_post_detail_unauthenticated(
        self,
        api_client,
        my_post,
    ):
        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 401

    def test_post_detail_not_found(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.get(url)

        assert response.status_code == 404

    # -------------------------
    # CREATE
    # -------------------------

    def test_post_create_authenticated(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "new post",
            "content": "new content",
            "status": True,
        }

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert Post.objects.filter(title="new post").exists()

    def test_post_create_unauthenticated(
        self,
        api_client,
    ):
        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "new post",
            "content": "new content",
            "status": True,
        }

        response = api_client.post(url, data)

        assert response.status_code == 401

    def test_post_create_invalid_data(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "content": "content without title",
        }

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_post_author_is_set_automatically(
        self,
        api_client,
        my_user,
        my_profile,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "author test",
            "content": "author content",
            "status": True,
        }

        response = api_client.post(url, data)

        assert response.status_code == 201

        post = Post.objects.get(title="author test")

        assert post.author == my_profile

    def test_user_cannot_set_author_manually(
        self,
        api_client,
        my_user,
        another_profile,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "manual author test",
            "content": "content",
            "status": True,
            "author": another_profile.pk,
        }

        response = api_client.post(url, data)

        assert response.status_code == 201

        post = Post.objects.get(title="manual author test")

        assert post.author == Profile.objects.get(user=my_user)

    # -------------------------
    # UPDATE
    # -------------------------

    def test_post_update_owner(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "updated title",
            "content": "updated content",
            "status": True,
        }

        response = api_client.put(url, data)

        assert response.status_code == 200

        my_post.refresh_from_db()

        assert my_post.title == "updated title"
        assert my_post.content == "updated content"

    def test_post_partial_update_owner(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "patched title",
        }

        response = api_client.patch(url, data)

        assert response.status_code == 200

        my_post.refresh_from_db()

        assert my_post.title == "patched title"

    def test_post_update_unauthenticated(
        self,
        api_client,
        my_post,
    ):
        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "updated title",
            "content": "updated content",
            "status": True,
        }

        response = api_client.put(url, data)

        assert response.status_code == 401

    def test_post_update_not_owner(
        self,
        api_client,
        another_user,
        my_post,
    ):
        api_client.force_authenticate(user=another_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "hacked title",
        }

        response = api_client.patch(url, data)

        assert response.status_code == 403

        my_post.refresh_from_db()

        assert my_post.title != "hacked title"

    def test_post_update_invalid_data(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        old_title = my_post.title

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "",
        }

        response = api_client.patch(url, data)

        assert response.status_code == 400

        my_post.refresh_from_db()

        assert my_post.title == old_title

    def test_post_update_not_found(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.patch(
            url,
            {"title": "test"},
        )

        assert response.status_code == 404

    # -------------------------
    # DELETE
    # -------------------------

    def test_post_delete_owner(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 204

        assert not Post.objects.filter(pk=my_post.pk).exists()

    def test_post_delete_unauthenticated(
        self,
        api_client,
        my_post,
    ):
        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 401

    def test_post_delete_not_owner(
        self,
        api_client,
        another_user,
        my_post,
    ):
        api_client.force_authenticate(user=another_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 403

        assert Post.objects.filter(pk=my_post.pk).exists()

    def test_post_delete_not_found(
        self,
        api_client,
        my_user,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.delete(url)

        assert response.status_code == 404

    # -------------------------
    # FILTER
    # -------------------------

    def test_filter_by_category(
        self,
        api_client,
        my_user,
        my_post,
        another_post,
        my_category,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"category": my_category.pk},
        )

        assert response.status_code == 200

        for post in response.data["results"]:
            assert post["category"]["id"] == my_category.pk

    def test_filter_by_author(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"author": my_post.author.pk},
        )

        assert response.status_code == 200

        for post in response.data["results"]:
            assert post["author"] == my_post.author.pk

    def test_filter_category_in(
        self,
        api_client,
        my_user,
        my_post,
        another_post,
        my_category,
        another_category,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"category__in": (f"{my_category.pk},{another_category.pk}")},
        )

        assert response.status_code == 200

    # -------------------------
    # SEARCH
    # -------------------------

    def test_search_by_title(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"search": "test post"},
        )

        assert response.status_code == 200

    def test_search_by_content(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"search": "test content"},
        )

        assert response.status_code == 200

    # -------------------------
    # ORDERING
    # -------------------------

    def test_ordering_created_at(
        self,
        api_client,
        my_user,
        my_post,
        another_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"ordering": "created_at"},
        )

        assert response.status_code == 200

    def test_ordering_created_at_descending(
        self,
        api_client,
        my_user,
        my_post,
        another_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(
            url,
            {"ordering": "-created_at"},
        )

        assert response.status_code == 200

    # -------------------------
    # SERIALIZER REPRESENTATION
    # -------------------------

    def test_list_representation_does_not_contain_content(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        post = response.data["results"][0]

        assert "content" not in post
        assert "snippest" in post
        assert "post_url" in post

    def test_detail_representation_contains_content(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        assert "content" in response.data
        assert "snippest" not in response.data
        assert "post_url" not in response.data

    def test_category_is_nested_in_post(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        assert isinstance(
            response.data["category"],
            dict,
        )

        assert response.data["category"]["id"] == (my_post.category.pk)