from django.urls import path

from ..views import (
    RegisterView,
    CustomAuthToken,
    CustomDiscardAuthToken,
    CustomJwtTokenObtainPairView,
    ChangePasswordView,
    ActivationView,
    ResendActivationEmail,
    ResetPasswordEmai,
    ResetPasswordView,
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Register
    path("registration/", RegisterView.as_view(), name="register"),
    # Change Password
    path(
        "change_password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
    # Reset Password
    path(
        "reset_password/",
        ResetPasswordEmai.as_view(),
        name="reset_password_email",
    ),
    path(
        "reset_password/confirm/<str:token>/",
        ResetPasswordView.as_view(),
        name="reset_password_confirm",
    ),
    # Token Authentication
    path("token-login/", CustomAuthToken.as_view(), name="login-token"),
    path(
        "token-destroy/",
        CustomDiscardAuthToken.as_view(),
        name="destroy-token",
    ),
    # Jwt Authentication
    path(
        "jwt/token/",
        CustomJwtTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # Activation
    path(
        "activation/confirm/<str:token>/",
        ActivationView.as_view(),
        name="activation_confirm",
    ),
    path(
        "activation/resend/",
        ResendActivationEmail.as_view(),
        name="resend_activation",
    ),
]
