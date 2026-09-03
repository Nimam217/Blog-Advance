'''import pytest

from accounts.models import User, Profile


@pytest.mark.django_db
class TestUserManager:

    def test_create_user_successfully(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        assert user.email == "test@gmail.com"
        assert user.check_password("@Asdf123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.is_verified is False

    def test_create_user_without_email(self):
        with pytest.raises(ValueError, match="The Email must be set"):
            User.objects.create_user(
                email="",
                password="@Asdf123",
            )

    def test_create_superuser_successfully(self):
        user = User.objects.create_superuser(
            email="admin@gmail.com",
            password="@Asdf123",
        )

        assert user.email == "admin@gmail.com"
        assert user.check_password("@Asdf123")
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.is_verified is True

    def test_create_superuser_requires_staff(self):
        with pytest.raises(
            ValueError,
            match="Superuser must have is_staff=True.",
        ):
            User.objects.create_superuser(
                email="admin@gmail.com",
                password="@Asdf123",
                is_staff=False,
            )

    def test_create_superuser_requires_superuser(self):
        with pytest.raises(
            ValueError,
            match="Superuser must have is_superuser=True.",
        ):
            User.objects.create_superuser(
                email="admin@gmail.com",
                password="@Asdf123",
                is_superuser=False,
            )

    def test_user_str(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        assert str(user) == "test@gmail.com"


@pytest.mark.django_db
class TestProfileModel:

    def test_profile_created_automatically(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile = Profile.objects.get(user=user)

        assert profile.user == user

    def test_profile_default_values(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile = Profile.objects.get(user=user)

        assert profile.image.name == ""
        assert profile.first_name == ""
        assert profile.last_name == ""
        assert profile.description == ""

    def test_profile_fields(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile = Profile.objects.get(user=user)

        profile.first_name = "Nima"
        profile.last_name = "Aghahadi"
        profile.description = "Test description"
        profile.save()

        profile.refresh_from_db()

        assert profile.first_name == "Nima"
        assert profile.last_name == "Aghahadi"
        assert profile.description == "Test description"

    def test_profile_one_to_one_relation(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile = Profile.objects.get(user=user)

        assert user.profile == profile

    def test_profile_deleted_when_user_deleted(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile_id = user.profile.id

        user.delete()

        assert not Profile.objects.filter(id=profile_id).exists()'''