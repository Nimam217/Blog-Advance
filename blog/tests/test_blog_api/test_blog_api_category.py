'''import pytest

from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from blog.models import Category


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def category_user(db):
    return User.objects.create_user(
        email="category_user@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def category(db):
    return Category.objects.create(
        name="test category",
    )


@pytest.mark.django_db
class TestCategoryAPI:

    # -------------------------
    # LIST
    # -------------------------

    def test_category_list_anonymous(
        self,
        api_client,
        category,
    ):
        url = reverse("blog:api_v1:category-list")

        response = api_client.get(url)

        assert response.status_code == 200

    def test_category_list_authenticated(
        self,
        api_client,
        category_user,
        category,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse("blog:api_v1:category-list")

        response = api_client.get(url)

        assert response.status_code == 200

    # -------------------------
    # RETRIEVE
    # -------------------------

    def test_category_detail_anonymous(
        self,
        api_client,
        category,
    ):
        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        response = api_client.get(url)

        assert response.status_code == 200

    def test_category_detail_not_found(
        self,
        api_client,
    ):
        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.get(url)

        assert response.status_code == 404

    # -------------------------
    # CREATE
    # -------------------------

    def test_category_create_authenticated(
        self,
        api_client,
        category_user,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse("blog:api_v1:category-list")

        data = {
            "name": "new category",
        }

        response = api_client.post(
            url,
            data,
        )

        assert response.status_code == 201

        assert Category.objects.filter(name="new category").exists()

    def test_category_create_anonymous(
        self,
        api_client,
    ):
        url = reverse("blog:api_v1:category-list")

        data = {
            "name": "anonymous category",
        }

        response = api_client.post(
            url,
            data,
        )

        assert response.status_code == 401

        assert not Category.objects.filter(name="anonymous category").exists()

    def test_category_create_invalid_data(
        self,
        api_client,
        category_user,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse("blog:api_v1:category-list")

        data = {
            "name": "",
        }

        response = api_client.post(
            url,
            data,
        )

        assert response.status_code == 400

    # -------------------------
    # UPDATE
    # -------------------------

    def test_category_update_authenticated(
        self,
        api_client,
        category_user,
        category,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        data = {
            "name": "updated category",
        }

        response = api_client.put(
            url,
            data,
        )

        assert response.status_code == 200

        category.refresh_from_db()

        assert category.name == "updated category"

    def test_category_partial_update_authenticated(
        self,
        api_client,
        category_user,
        category,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        data = {
            "name": "patched category",
        }

        response = api_client.patch(
            url,
            data,
        )

        assert response.status_code == 200

        category.refresh_from_db()

        assert category.name == "patched category"

    def test_category_update_anonymous(
        self,
        api_client,
        category,
    ):
        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        data = {
            "name": "anonymous update",
        }

        response = api_client.put(
            url,
            data,
        )

        assert response.status_code == 401

        category.refresh_from_db()

        assert category.name != "anonymous update"

    def test_category_update_invalid_data(
        self,
        api_client,
        category_user,
        category,
    ):
        api_client.force_authenticate(user=category_user)

        old_name = category.name

        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        data = {
            "name": "",
        }

        response = api_client.put(
            url,
            data,
        )

        assert response.status_code == 400

        category.refresh_from_db()

        assert category.name == old_name

    # -------------------------
    # DELETE
    # -------------------------

    def test_category_delete_authenticated(
        self,
        api_client,
        category_user,
        category,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 204

        assert not Category.objects.filter(pk=category.pk).exists()

    def test_category_delete_anonymous(
        self,
        api_client,
        category,
    ):
        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": category.pk},
        )

        response = api_client.delete(url)

        assert response.status_code == 401

        assert Category.objects.filter(pk=category.pk).exists()

    def test_category_delete_not_found(
        self,
        api_client,
        category_user,
    ):
        api_client.force_authenticate(user=category_user)

        url = reverse(
            "blog:api_v1:category-detail",
            kwargs={"pk": 999999},
        )

        response = api_client.delete(url)

        assert response.status_code == 404
'''