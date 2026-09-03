import pytest
from rest_framework.test import APIRequestFactory

from accounts.models import Profile, User
from accounts.api.v1.serializers import (
    RegisterViewSerializer,
    CustomAuthTokenSerializer,
    CustomJwtTokenPairViewSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ResendActivationSerializer,
    ResetPasswordEmaiSerializer,
    ResetPasswordViewSerializer,
)
from rest_framework.exceptions import AuthenticationFailed


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="test@gmail.com",
        password="@Asdf123",
    )


@pytest.fixture
def verified_user(user):
    user.is_verified = True
    user.save()
    return user


@pytest.fixture
def request_factory():
    return APIRequestFactory()


# =========================================================
# RegisterViewSerializer
# =========================================================

@pytest.mark.django_db
class TestRegisterViewSerializer:

    def test_valid_data(self):
        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Asdf123",
        }

        serializer = RegisterViewSerializer(data=data)

        assert serializer.is_valid() is True

    def test_password_confirmation_mismatch(self):
        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Wrong123",
        }

        serializer = RegisterViewSerializer(data=data)

        assert serializer.is_valid() is False
        assert "detail" in serializer.errors

    def test_weak_password(self):
        data = {
            "email": "newuser@gmail.com",
            "password": "123",
            "password_confirmation": "123",
        }

        serializer = RegisterViewSerializer(data=data)

        assert serializer.is_valid() is False
        assert "password" in serializer.errors

    def test_required_fields(self):
        serializer = RegisterViewSerializer(data={})

        assert serializer.is_valid() is False
        assert "email" in serializer.errors
        assert "password" in serializer.errors
        assert "password_confirmation" in serializer.errors

    def test_create_user(self):
        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Asdf123",
        }

        serializer = RegisterViewSerializer(data=data)

        assert serializer.is_valid() is True

        user = serializer.save()

        assert user.email == "newuser@gmail.com"
        assert user.check_password("@Asdf123")

    def test_password_confirmation_is_not_saved(self):
        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Asdf123",
        }

        serializer = RegisterViewSerializer(data=data)

        assert serializer.is_valid() is True

        user = serializer.save()

        assert not hasattr(user, "password_confirmation")


# =========================================================
# CustomAuthTokenSerializer
# =========================================================

@pytest.mark.django_db
class TestCustomAuthTokenSerializer:

    def test_valid_credentials(
        self,
        user,
        request_factory,
    ):
        user.is_verified = True
        user.save()

        request = request_factory.post("/api/login/")

        data = {
            "email": "test@gmail.com",
            "password": "@Asdf123",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is True
        assert serializer.validated_data["user"] == user

    def test_invalid_password(
        self,
        user,
        request_factory,
    ):
        user.is_verified = True
        user.save()

        request = request_factory.post("/api/login/")

        data = {
            "email": "test@gmail.com",
            "password": "WrongPassword123",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False

    def test_unverified_user(
        self,
        user,
        request_factory,
    ):
        request = request_factory.post("/api/login/")

        data = {
            "email": "test@gmail.com",
            "password": "@Asdf123",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False
        assert "detail" in serializer.errors

    def test_user_does_not_exist(
        self,
        request_factory,
    ):
        request = request_factory.post("/api/login/")

        data = {
            "email": "notexist@gmail.com",
            "password": "@Asdf123",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False

    def test_missing_email(
        self,
        request_factory,
    ):
        request = request_factory.post("/api/login/")

        data = {
            "password": "@Asdf123",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False

    def test_missing_password(
        self,
        request_factory,
    ):
        request = request_factory.post("/api/login/")

        data = {
            "email": "test@gmail.com",
        }

        serializer = CustomAuthTokenSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False


# =========================================================
# CustomJwtTokenPairViewSerializer
# =========================================================

@pytest.mark.django_db
class TestCustomJwtTokenPairViewSerializer:

    def test_valid_verified_user(self, verified_user):
        data = {
            "email": "test@gmail.com",
            "password": "@Asdf123",
        }

        serializer = CustomJwtTokenPairViewSerializer(data=data)

        assert serializer.is_valid() is True

        assert "access" in serializer.validated_data
        assert "refresh" in serializer.validated_data
        assert "user" in serializer.validated_data

        assert serializer.validated_data["user"]["id"] == verified_user.id
        assert serializer.validated_data["user"]["email"] == verified_user.email

    def test_unverified_user(self, user):
        data = {
            "email": "test@gmail.com",
            "password": "@Asdf123",
        }

        serializer = CustomJwtTokenPairViewSerializer(data=data)

        assert serializer.is_valid() is False
        assert "detail" in serializer.errors

    def test_invalid_password(self, verified_user):
        data = {
            "email": "test@gmail.com",
            "password": "WrongPassword123",
        }

        serializer = CustomJwtTokenPairViewSerializer(data=data)

        with pytest.raises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)


# =========================================================
# ChangePasswordSerializer
# =========================================================

@pytest.mark.django_db
class TestChangePasswordSerializer:

    def test_valid_data(self, user, request_factory):
        request = request_factory.post("/api/change-password/")
        request.user = user

        data = {
            "old_password": "@Asdf123",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        serializer = ChangePasswordSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is True

    def test_password_confirmation_mismatch(
        self,
        user,
        request_factory,
    ):
        request = request_factory.post("/api/change-password/")
        request.user = user

        data = {
            "old_password": "@Asdf123",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@WrongPassword123",
        }

        serializer = ChangePasswordSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False
        assert "new_password_confirmation" in serializer.errors

    def test_weak_new_password(
        self,
        user,
        request_factory,
    ):
        request = request_factory.post("/api/change-password/")
        request.user = user

        data = {
            "old_password": "@Asdf123",
            "new_password": "123",
            "new_password_confirmation": "123",
        }

        serializer = ChangePasswordSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False
        assert "new_password" in serializer.errors

    def test_missing_old_password(
        self,
        user,
        request_factory,
    ):
        request = request_factory.post("/api/change-password/")
        request.user = user

        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        serializer = ChangePasswordSerializer(
            data=data,
            context={"request": request},
        )

        assert serializer.is_valid() is False
        assert "old_password" in serializer.errors


# =========================================================
# ProfileSerializer
# =========================================================

@pytest.mark.django_db
class TestProfileSerializer:

    def test_profile_serialization(self, user):
        profile = Profile.objects.get(user=user)

        profile.first_name = "Nima"
        profile.last_name = "Aghahadi"
        profile.description = "Test description"
        profile.save()

        serializer = ProfileSerializer(profile)

        data = serializer.data

        assert data["id"] == profile.id
        assert data["email"] == user.email
        assert data["first_name"] == "Nima"
        assert data["last_name"] == "Aghahadi"
        assert data["description"] == "Test description"

    def test_email_is_read_only(self, user):
        serializer = ProfileSerializer()

        assert serializer.fields["email"].read_only is True

    def test_update_profile(self, user):
        profile = Profile.objects.get(user=user)

        data = {
            "first_name": "Nima",
            "last_name": "Test",
            "description": "Updated description",
        }

        serializer = ProfileSerializer(
            profile,
            data=data,
            partial=True,
        )

        assert serializer.is_valid() is True

        updated_profile = serializer.save()

        assert updated_profile.first_name == "Nima"
        assert updated_profile.last_name == "Test"
        assert updated_profile.description == "Updated description"


# =========================================================
# ResendActivationSerializer
# =========================================================

@pytest.mark.django_db
class TestResendActivationSerializer:

    def test_valid_email(self, user):
        data = {
            "email": "test@gmail.com",
        }

        serializer = ResendActivationSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data["user"] == user

    def test_user_does_not_exist(self):
        data = {
            "email": "notexist@gmail.com",
        }

        serializer = ResendActivationSerializer(data=data)

        assert serializer.is_valid() is False
        assert "detail" in serializer.errors

    def test_email_is_required(self):
        serializer = ResendActivationSerializer(data={})

        assert serializer.is_valid() is False
        assert "email" in serializer.errors


# =========================================================
# ResetPasswordEmaiSerializer
# =========================================================

@pytest.mark.django_db
class TestResetPasswordEmaiSerializer:

    def test_valid_email(self, user):
        data = {
            "email": "test@gmail.com",
        }

        serializer = ResetPasswordEmaiSerializer(data=data)

        assert serializer.is_valid() is True
        assert serializer.validated_data["user"] == user

    def test_user_does_not_exist(self):
        data = {
            "email": "notexist@gmail.com",
        }

        serializer = ResetPasswordEmaiSerializer(data=data)

        assert serializer.is_valid() is False
        assert "detail" in serializer.errors

    def test_email_is_required(self):
        serializer = ResetPasswordEmaiSerializer(data={})

        assert serializer.is_valid() is False
        assert "email" in serializer.errors


# =========================================================
# ResetPasswordViewSerializer
# =========================================================

@pytest.mark.django_db
class TestResetPasswordViewSerializer:

    def test_valid_data(self):
        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        serializer = ResetPasswordViewSerializer(data=data)

        assert serializer.is_valid() is True

    def test_password_confirmation_mismatch(self):
        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@WrongPassword123",
        }

        serializer = ResetPasswordViewSerializer(data=data)

        assert serializer.is_valid() is False
        assert "new_password_confirmation" in serializer.errors

    def test_weak_password(self):
        data = {
            "new_password": "123",
            "new_password_confirmation": "123",
        }

        serializer = ResetPasswordViewSerializer(data=data)

        assert serializer.is_valid() is False
        assert "new_password_confirmation" in serializer.errors

    def test_required_fields(self):
        serializer = ResetPasswordViewSerializer(data={})

        assert serializer.is_valid() is False

        assert "new_password" in serializer.errors
        assert "new_password_confirmation" in serializer.errors