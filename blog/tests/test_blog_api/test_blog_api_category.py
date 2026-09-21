import pytest
from rest_framework.test import APIClient

from accounts.models import User
from blog.models import Category


@pytest.mark.django_db
class TestCategoryAPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="category@gmail.com",
            password="@ASDf123",
        )

        self.admin = User.objects.create_superuser(
            email="admin@gmail.com",
            password="@ASDf123",
        )

        self.category = Category.objects.create(
            name="Django",
        )

        self.url = "/blog/api/v1/category/"

    def test_category_list_successfully(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        assert response.status_code == 200

        # ساختار paginated
        assert response.data["total_category"] == 1
        assert response.data["total_page"] == 1
        assert len(response.data["results"]) == 1

        assert response.data["results"][0] == {
            "id": self.category.id,
            "name": "Django",
        }

    def test_category_detail_successfully(self):
        self.client.force_authenticate(user=self.user)

        url = f"{self.url}{self.category.id}/"

        response = self.client.get(url)

        assert response.status_code == 200

        assert response.data["id"] == self.category.id
        assert response.data["name"] == "Django"

    # -------------------------
    # POST - NOT AUTHENTICATED
    # -------------------------

    def test_category_create_not_authenticated(self):
        response = self.client.post(
            self.url,
            {"name": "Python"},
            format="json",
        )

        assert response.status_code == 401

        assert not Category.objects.filter(name="Python").exists()

    # -------------------------
    # POST - AUTHENTICATED USER
    # -------------------------

    def test_category_create_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.url,
            {"name": "Python"},
            format="json",
        )

        assert response.status_code == 403

        assert not Category.objects.filter(name="Python").exists()

    # -------------------------
    # POST - ADMIN
    # -------------------------

    def test_category_create_admin(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            self.url,
            {"name": "Python"},
            format="json",
        )

        assert response.status_code == 201

        assert Category.objects.filter(name="Python").exists()

        assert response.data["name"] == "Python"

    # -------------------------
    # PUT - ADMIN
    # -------------------------

    def test_category_update_admin(self):
        self.client.force_authenticate(user=self.admin)

        url = f"{self.url}{self.category.id}/"

        response = self.client.put(
            url,
            {"name": "Django REST Framework"},
            format="json",
        )

        assert response.status_code == 200

        self.category.refresh_from_db()

        assert self.category.name == "Django REST Framework"

    # -------------------------
    # PATCH - ADMIN
    # -------------------------

    def test_category_partial_update_admin(self):
        self.client.force_authenticate(user=self.admin)

        url = f"{self.url}{self.category.id}/"

        response = self.client.patch(
            url,
            {"name": "DRF"},
            format="json",
        )

        assert response.status_code == 200

        self.category.refresh_from_db()

        assert self.category.name == "DRF"

    # -------------------------
    # PUT - NORMAL USER
    # -------------------------

    def test_category_update_normal_user(self):
        self.client.force_authenticate(user=self.user)

        url = f"{self.url}{self.category.id}/"

        response = self.client.put(
            url,
            {"name": "Hacked"},
            format="json",
        )

        assert response.status_code == 403

        self.category.refresh_from_db()

        assert self.category.name == "Django"

    # -------------------------
    # DELETE - ADMIN
    # -------------------------

    def test_category_delete_admin(self):
        self.client.force_authenticate(user=self.admin)

        url = f"{self.url}{self.category.id}/"

        response = self.client.delete(url)

        assert response.status_code == 204

        assert not Category.objects.filter(id=self.category.id).exists()

    # -------------------------
    # DELETE - NORMAL USER
    # -------------------------

    def test_category_delete_normal_user(self):
        self.client.force_authenticate(user=self.user)

        url = f"{self.url}{self.category.id}/"

        response = self.client.delete(url)

        assert response.status_code == 403

        assert Category.objects.filter(id=self.category.id).exists()
