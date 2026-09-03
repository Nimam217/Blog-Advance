'''import pytest
from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Profile


# =========================================================
# Fixtures
# =========================================================

@pytest.fixture
def api_client():
    return APIClient()


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
def auth_client(api_client, verified_user):
    api_client.force_authenticate(user=verified_user)
    return api_client


# =========================================================
# Register
# =========================================================

@pytest.mark.django_db
class TestRegisterView:

    @patch("accounts.api.v1.views.EmailThread.start")
    def test_register_successfully(self, mock_start, api_client):

        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Asdf123",
        }

        url = reverse(
            "accounts:accounts-api-v1:register"
        )

        response = api_client.post(url, data)

        assert response.status_code == 201
        assert response.data["email"] == "newuser@gmail.com"

        user = User.objects.get(
            email="newuser@gmail.com"
        )

        assert Profile.objects.filter(
            user=user
        ).exists()

        assert Token.objects.filter(
            user=user
        ).exists()

        mock_start.assert_called_once()

    @patch("accounts.api.v1.views.EmailThread.start")
    def test_register_password_mismatch(
        self,
        mock_start,
        api_client,
    ):

        data = {
            "email": "newuser@gmail.com",
            "password": "@Asdf123",
            "password_confirmation": "@Different123",
        }

        url = reverse(
            "accounts:accounts-api-v1:register"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400

        assert not User.objects.filter(
            email="newuser@gmail.com"
        ).exists()

        mock_start.assert_not_called()


# =========================================================
# Custom Auth Token
# =========================================================

@pytest.mark.django_db
class TestCustomAuthToken:

    def test_login_successfully(
        self,
        api_client,
        verified_user,
    ):

        data = {
            "email": verified_user.email,
            "password": "@Asdf123",
        }

        url = reverse(
            "accounts:accounts-api-v1:login-token"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

        assert "token" in response.data
        assert "user_id" in response.data
        assert "email" in response.data

        assert response.data["user_id"] == verified_user.id
        assert response.data["email"] == verified_user.email

    def test_login_unverified_user(
        self,
        api_client,
        user,
    ):

        data = {
            "email": user.email,
            "password": "@Asdf123",
        }

        url = reverse(
            "accounts:accounts-api-v1:login-token"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_login_invalid_password(
        self,
        api_client,
        verified_user,
    ):

        data = {
            "email": verified_user.email,
            "password": "wrong-password",
        }

        url = reverse(
            "accounts:accounts-api-v1:login-token"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400


# =========================================================
# Destroy Token / Logout
# =========================================================

@pytest.mark.django_db
class TestCustomDiscardAuthToken:

    def test_logout_successfully(
        self,
        api_client,
        verified_user,
    ):

        token = Token.objects.get(
            user=verified_user
        )

        api_client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

        url = reverse(
            "accounts:accounts-api-v1:destroy-token"
        )

        response = api_client.post(url)

        assert response.status_code == 204

        assert not Token.objects.filter(
            user=verified_user
        ).exists()

    def test_logout_unauthenticated(
        self,
        api_client,
    ):

        url = reverse(
            "accounts:accounts-api-v1:destroy-token"
        )

        response = api_client.post(url)

        assert response.status_code == 401


# =========================================================
# JWT
# =========================================================

@pytest.mark.django_db
class TestCustomJwtTokenObtainPairView:

    def test_jwt_login_successfully(
        self,
        api_client,
        verified_user,
    ):

        data = {
            "email": verified_user.email,
            "password": "@Asdf123",
        }

        url = reverse(
            "accounts:accounts-api-v1:token_obtain_pair"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

        assert "access" in response.data
        assert "refresh" in response.data
        assert "user" in response.data

        assert response.data["user"]["id"] == (
            verified_user.id
        )

        assert response.data["user"]["email"] == (
            verified_user.email
        )

    def test_jwt_login_unverified_user(
        self,
        api_client,
        user,
    ):

        data = {
            "email": user.email,
            "password": "@Asdf123",
        }

        url = reverse(
            "accounts:accounts-api-v1:token_obtain_pair"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_jwt_login_invalid_password(
        self,
        api_client,
        verified_user,
    ):

        data = {
            "email": verified_user.email,
            "password": "wrong-password",
        }

        url = reverse(
            "accounts:accounts-api-v1:token_obtain_pair"
        )

        response = api_client.post(url, data)

        assert response.status_code == 401

    def test_jwt_refresh_successfully(
            self,
            api_client,
            verified_user,
    ):
        refresh = RefreshToken.for_user(verified_user)

        data = {
            "refresh": str(refresh),
        }

        url = reverse(
            "accounts:accounts-api-v1:token_refresh"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200
        assert "access" in response.data

    def test_jwt_refresh_invalid_token(self, api_client):
        data = {
            "refresh": "invalid-refresh-token",
        }

        url = reverse(
            "accounts:accounts-api-v1:token_refresh"
        )

        response = api_client.post(url, data)

        assert response.status_code == 401

    def test_jwt_verify_successfully(self, api_client, verified_user):
        refresh = RefreshToken.for_user(verified_user)
        access_token = str(refresh.access_token)

        data = {
            "token": access_token
        }

        url = reverse(
            "accounts:accounts-api-v1:token_verify"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

    def test_jwt_verify_with_invalid_token(self, api_client):
        data = {
            "token": "invalid-token"
        }

        url = reverse(
            "accounts:accounts-api-v1:token_verify"
        )

        response = api_client.post(url, data)

        assert response.status_code in [400, 401]

    def test_jwt_verify_without_token(self, api_client):
        url = reverse(
            "accounts:accounts-api-v1:token_verify"
        )

        response = api_client.post(url, {})

        assert response.status_code == 400


# =========================================================
# Change Password
# =========================================================

@pytest.mark.django_db
class TestChangePasswordView:

    def test_change_password_successfully(
        self,
        auth_client,
        verified_user,
    ):

        data = {
            "old_password": "@Asdf123",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:change_password"
        )

        response = auth_client.put(url, data)

        assert response.status_code == 200

        assert response.data["status"] == "success"
        assert response.data["code"] == 200

        verified_user.refresh_from_db()

        assert verified_user.check_password(
            "@NewPassword123"
        )

    def test_change_password_wrong_old_password(
        self,
        auth_client,
    ):

        data = {
            "old_password": "wrong-password",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:change_password"
        )

        response = auth_client.put(url, data)

        assert response.status_code == 400
        assert "old_password" in response.data

    def test_change_password_confirmation_mismatch(
        self,
        auth_client,
    ):

        data = {
            "old_password": "@Asdf123",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@Different123",
        }

        url = reverse(
            "accounts:accounts-api-v1:change_password"
        )

        response = auth_client.put(url, data)

        assert response.status_code == 400

    def test_change_password_unauthenticated(
        self,
        api_client,
    ):

        data = {
            "old_password": "@Asdf123",
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:change_password"
        )

        response = api_client.put(url, data)

        assert response.status_code == 401


# =========================================================
# Profile
# =========================================================

@pytest.mark.django_db
class TestProfileView:

    def test_profile_get_successfully(
        self,
        auth_client,
        verified_user,
    ):

        url = reverse(
            "accounts:accounts-api-v1:profile"
        )

        response = auth_client.get(url)

        assert response.status_code == 200
        assert response.data["email"] == verified_user.email

    def test_profile_update_successfully(
        self,
        auth_client,
        verified_user,
    ):

        data = {
            "first_name": "Nima",
            "last_name": "Aghahadi",
            "description": "My description",
        }

        url = reverse(
            "accounts:accounts-api-v1:profile"
        )

        response = auth_client.patch(url, data)

        assert response.status_code == 200

        profile = Profile.objects.get(
            user=verified_user
        )

        assert profile.first_name == "Nima"
        assert profile.last_name == "Aghahadi"
        assert profile.description == "My description"

    def test_profile_unverified_user(
        self,
        api_client,
        user,
    ):

        api_client.force_authenticate(user=user)

        url = reverse(
            "accounts:accounts-api-v1:profile"
        )

        response = api_client.get(url)

        assert response.status_code == 403

    def test_profile_unauthenticated(
        self,
        api_client,
    ):

        url = reverse(
            "accounts:accounts-api-v1:profile"
        )

        response = api_client.get(url)

        assert response.status_code == 401


# =========================================================
# Activation
# =========================================================

@pytest.mark.django_db
class TestActivationView:

    def test_activation_successfully(
        self,
        api_client,
        user,
    ):

        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        url = reverse(
            "accounts:accounts-api-v1:activation_confirm",
            kwargs={"token": token},
        )

        response = api_client.get(url)

        assert response.status_code == 200

        assert response.data["detail"] == (
            "successfully activated"
        )

        user.refresh_from_db()

        assert user.is_verified is True

    def test_activation_already_verified(
        self,
        api_client,
        verified_user,
    ):

        refresh = RefreshToken.for_user(
            verified_user
        )

        token = str(refresh.access_token)

        url = reverse(
            "accounts:accounts-api-v1:activation_confirm",
            kwargs={"token": token},
        )

        response = api_client.get(url)

        assert response.status_code == 400

        assert response.data["detail"] == (
            "user have been already verified"
        )

    def test_activation_invalid_token(
        self,
        api_client,
    ):

        url = reverse(
            "accounts:accounts-api-v1:activation_confirm",
            kwargs={"token": "invalid-token"},
        )

        response = api_client.get(url)

        assert response.status_code == 400

        assert response.data["detail"] == (
            "invalid token"
        )


# =========================================================
# Resend Activation Email
# =========================================================

@pytest.mark.django_db
class TestResendActivationEmail:

    @patch("accounts.api.v1.views.EmailThread.start")
    def test_resend_activation_successfully(
        self,
        mock_start,
        api_client,
        user,
    ):

        data = {
            "email": user.email,
        }

        url = reverse(
            "accounts:accounts-api-v1:resend_activation"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

        assert response.data["detail"] == (
            "email has been sent successfully"
        )

        mock_start.assert_called_once()

    def test_resend_activation_nonexistent_user(
        self,
        api_client,
    ):

        data = {
            "email": "doesnotexist@gmail.com",
        }

        url = reverse(
            "accounts:accounts-api-v1:resend_activation"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400


# =========================================================
# Reset Password Email
# =========================================================

@pytest.mark.django_db
class TestResetPasswordEmail:

    @patch("accounts.api.v1.views.EmailThread.start")
    def test_reset_password_email_successfully(
        self,
        mock_start,
        api_client,
        verified_user,
    ):

        data = {
            "email": verified_user.email,
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_email"
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

        assert response.data["detail"] == (
            "email has been sent successfully"
        )

        mock_start.assert_called_once()

    def test_reset_password_email_unverified_user(
        self,
        api_client,
        user,
    ):

        data = {
            "email": user.email,
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_email"
        )

        response = api_client.post(url, data)

        assert response.status_code == 401

    def test_reset_password_email_nonexistent_user(
        self,
        api_client,
    ):

        data = {
            "email": "doesnotexist@gmail.com",
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_email"
        )

        response = api_client.post(url, data)

        assert response.status_code == 400


# =========================================================
# Reset Password Confirm
# =========================================================

@pytest.mark.django_db
class TestResetPasswordView:

    def test_reset_password_successfully(
        self,
        api_client,
        verified_user,
    ):

        refresh = RefreshToken.for_user(
            verified_user
        )

        token = str(refresh.access_token)

        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_confirm",
            kwargs={"token": token},
        )

        response = api_client.post(url, data)

        assert response.status_code == 200

        assert response.data["detail"] == (
            "password has been reset successfully"
        )

        verified_user.refresh_from_db()

        assert verified_user.check_password(
            "@NewPassword123"
        )

    def test_reset_password_password_mismatch(
        self,
        api_client,
        verified_user,
    ):

        refresh = RefreshToken.for_user(
            verified_user
        )

        token = str(refresh.access_token)

        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@Different123",
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_confirm",
            kwargs={"token": token},
        )

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_reset_password_invalid_token(
        self,
        api_client,
    ):

        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_confirm",
            kwargs={"token": "invalid-token"},
        )

        response = api_client.post(url, data)

        assert response.status_code == 400

    def test_reset_password_unverified_user(
        self,
        api_client,
        user,
    ):

        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)

        data = {
            "new_password": "@NewPassword123",
            "new_password_confirmation": "@NewPassword123",
        }

        url = reverse(
            "accounts:accounts-api-v1:reset_password_confirm",
            kwargs={"token": token},
        )

        response = api_client.post(url, data)

        assert response.status_code == 401'''