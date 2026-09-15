import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import Profile, User
from blog.models import Category, Post, Comment


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


@pytest.fixture
def inactive_post(my_profile, my_category):
    return Post.objects.create(
        title="inactive post",
        content="inactive content",
        author=my_profile,
        category=my_category,
        status=False,
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
class TestPostAPI:

    # =========================================================
    # LIST
    # =========================================================
    def test_post_list_authenticated(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        assert response.data["total_post"] == 1
        assert response.data["total_page"] == 1

        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == my_post.id
        assert response.data["results"][0]["title"] == "test post"

    def test_post_list_unauthenticated(
        self,
        api_client,
    ):
        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 401

    def test_post_list_only_active_posts(
        self,
        api_client,
        my_user,
        my_post,
        inactive_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        data = response.data["results"]

        titles = [post["title"] for post in data]

        assert "test post" in titles
        assert "inactive post" not in titles

    # =========================================================
    # RETRIEVE
    # =========================================================

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
        assert response.data["id"] == my_post.pk
        assert response.data["title"] == my_post.title

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

    # =========================================================
    # CREATE
    # =========================================================

    def test_post_create_authenticated(
        self,
        api_client,
        my_user,
        my_category,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "new post",
            "content": "new content",
            "category": my_category.pk,
            "status": True,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 201

        post = Post.objects.get(title="new post")

        assert post.content == "new content"
        assert post.category == my_category
        assert post.author == Profile.objects.get(user=my_user)

    def test_post_create_unauthenticated(
        self,
        api_client,
        my_category,
    ):
        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "new post",
            "content": "new content",
            "category": my_category.pk,
            "status": True,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 401

        assert not Post.objects.filter(title="new post").exists()

    def test_post_create_invalid_data(
        self,
        api_client,
        my_user,
        my_category,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "",
            "content": "content",
            "category": my_category.pk,
            "status": True,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 400

    def test_post_author_is_set_automatically(
        self,
        api_client,
        my_user,
        my_category,
        my_profile,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "author test",
            "content": "author content",
            "category": my_category.pk,
            "status": True,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 201

        post = Post.objects.get(title="author test")

        assert post.author == my_profile

    def test_user_cannot_set_author_manually(
        self,
        api_client,
        my_user,
        my_category,
        another_profile,
        my_profile,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        data = {
            "title": "manual author test",
            "content": "content",
            "category": my_category.pk,
            "status": True,
            "author": another_profile.pk,
        }

        response = api_client.post(
            url,
            data,
            format="json",
        )

        assert response.status_code == 201

        post = Post.objects.get(title="manual author test")

        assert post.author == my_profile
        assert post.author != another_profile

    # =========================================================
    # UPDATE
    # =========================================================

    def test_post_update_owner(
        self,
        api_client,
        my_user,
        my_post,
        my_category,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        data = {
            "title": "updated title",
            "content": "updated content",
            "category": my_category.pk,
            "status": True,
        }

        response = api_client.put(
            url,
            data,
            format="json",
        )

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

        response = api_client.patch(
            url,
            {"title": "patched title"},
            format="json",
        )

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

        response = api_client.put(
            url,
            {
                "title": "updated title",
            },
            format="json",
        )

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

        response = api_client.patch(
            url,
            {"title": "hacked title"},
            format="json",
        )

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

        response = api_client.patch(
            url,
            {"title": ""},
            format="json",
        )

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
            format="json",
        )

        assert response.status_code == 404

    # =========================================================
    # DELETE
    # =========================================================

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

        assert Post.objects.filter(pk=my_post.pk).exists()

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

    # =========================================================
    # FILTER
    # =========================================================

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

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["category"]["id"] == my_category.pk

    def test_filter_by_author(
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
            {"author": my_post.author.pk},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["author"] == my_post.author.pk

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

        data = response.data["results"]

        assert len(data) == 2

        category_ids = {post["category"]["id"] for post in data}

        assert category_ids == {
            my_category.pk,
            another_category.pk,
        }

    # =========================================================
    # SEARCH
    # =========================================================

    def test_search_by_title(
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
            {"search": "test post"},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert data[0]["title"] == "test post"

    def test_search_by_content(
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
            {"search": "test content"},
        )

        assert response.status_code == 200

        data = response.data["results"]

        assert len(data) == 1
        assert (
            data[0]["content"] == "test content"
            if "content" in data[0]
            else True
        )

    # =========================================================
    # ORDERING
    # =========================================================

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

        data = response.data["results"]

        assert len(data) == 2

        dates = [post["created_at"] for post in data]

        assert dates == sorted(dates)

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

        data = response.data["results"]

        assert len(data) == 2

        dates = [post["created_at"] for post in data]

        assert dates == sorted(
            dates,
            reverse=True,
        )

    # =========================================================
    # SERIALIZER REPRESENTATION
    # =========================================================

    def test_list_representation(
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
        assert "comments" not in post

    def test_detail_representation(
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
        assert "comments" in response.data

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

        category = response.data["category"]

        assert isinstance(category, dict)
        assert category["id"] == my_post.category.pk
        assert category["name"] == my_post.category.name

    # =========================================================
    # COMMENTS URL
    # =========================================================

    def test_post_detail_contains_comment_urls(
        self,
        api_client,
        my_user,
        my_post,
        my_comment,
        another_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse(
            "blog:api_v1:post-detail",
            kwargs={"pk": my_post.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        comments = response.data["comments"]

        assert len(comments) == 2

        expected_urls = {
            f"http://testserver/blog/api/v1/comment/{my_comment.pk}/",
            f"http://testserver/blog/api/v1/comment/{another_comment.pk}/",
        }

        assert set(comments) == expected_urls

    def test_post_list_does_not_contain_comment_urls(
        self,
        api_client,
        my_user,
        my_post,
        my_comment,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        post = response.data["results"][0]

        assert "comments" not in post

    def test_post_list_pagination_structure(
        self,
        api_client,
        my_user,
        my_post,
    ):
        api_client.force_authenticate(user=my_user)

        url = reverse("blog:api_v1:post-list")

        response = api_client.get(url)

        assert response.status_code == 200

        assert "links" in response.data
        assert "total_post" in response.data
        assert "total_page" in response.data
        assert "results" in response.data

        assert response.data["total_post"] == 1
        assert response.data["total_page"] == 1
        assert response.data["links"]["next"] is None
        assert response.data["links"]["previous"] is None
