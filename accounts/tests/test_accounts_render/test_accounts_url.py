'''import pytest

from django.urls import reverse, resolve

from accounts.api.v1.views import (
    RegisterView,
    ChangePasswordView,
    ResetPasswordEmai,
    ResetPasswordView,
    CustomAuthToken,
    CustomDiscardAuthToken,
    CustomJwtTokenObtainPairView,
    ActivationView,
    ResendActivationEmail,
    ProfileView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)


@pytest.mark.django_db
class TestAccountsURLs:

    def test_register_url(self):
        url = reverse("accounts:accounts-api-v1:register")

        assert url == "/accounts/api/v1/registration/"
        assert resolve(url).func.view_class == RegisterView

    def test_change_password_url(self):
        url = reverse("accounts:accounts-api-v1:change_password")

        assert url == "/accounts/api/v1/change_password/"
        assert resolve(url).func.view_class == ChangePasswordView

    def test_reset_password_email_url(self):
        url = reverse("accounts:accounts-api-v1:reset_password_email")

        assert url == "/accounts/api/v1/reset_password/"
        assert resolve(url).func.view_class == ResetPasswordEmai

    def test_reset_password_confirm_url(self):
        url = reverse(
            "accounts:accounts-api-v1:reset_password_confirm",
            kwargs={"token": "test-token"},
        )

        assert url == "/accounts/api/v1/reset_password/confirm/test-token/"
        assert resolve(url).func.view_class == ResetPasswordView

    def test_token_login_url(self):
        url = reverse("accounts:accounts-api-v1:login-token")

        assert url == "/accounts/api/v1/token-login/"
        assert resolve(url).func.view_class == CustomAuthToken

    def test_token_destroy_url(self):
        url = reverse("accounts:accounts-api-v1:destroy-token")

        assert url == "/accounts/api/v1/token-destroy/"
        assert resolve(url).func.view_class == CustomDiscardAuthToken

    def test_jwt_token_url(self):
        url = reverse("accounts:accounts-api-v1:token_obtain_pair")

        assert url == "/accounts/api/v1/jwt/token/"
        assert resolve(url).func.view_class == CustomJwtTokenObtainPairView

    def test_jwt_refresh_url(self):
        url = reverse("accounts:accounts-api-v1:token_refresh")

        assert url == "/accounts/api/v1/jwt/refresh/"
        assert resolve(url).func.view_class == TokenRefreshView

    def test_jwt_verify_url(self):
        url = reverse("accounts:accounts-api-v1:token_verify")

        assert url == "/accounts/api/v1/jwt/verify/"
        assert resolve(url).func.view_class == TokenVerifyView

    def test_activation_confirm_url(self):
        url = reverse(
            "accounts:accounts-api-v1:activation_confirm",
            kwargs={"token": "test-token"},
        )

        assert url == "/accounts/api/v1/activation/confirm/test-token/"
        assert resolve(url).func.view_class == ActivationView

    def test_activation_resend_url(self):
        url = reverse("accounts:accounts-api-v1:resend_activation")

        assert url == "/accounts/api/v1/activation/resend/"
        assert resolve(url).func.view_class == ResendActivationEmail

    def test_profile_url(self):
        url = reverse("accounts:accounts-api-v1:profile")

        assert url == "/accounts/api/v1/profile/"
        assert resolve(url).func.view_class == ProfileView'''