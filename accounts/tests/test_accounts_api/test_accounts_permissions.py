import pytest
from accounts.models import User
from accounts.api.v1.permissions import IsOwnerAndIsVerified


@pytest.fixture
def verified_user(db):
    return User.objects.create_user(
        email="verified@example.com",
        password="@Asdf123",
        is_verified=True,
    )


@pytest.fixture
def unverified_user(db):
    return User.objects.create_user(
        email="unverified@example.com",
        password="@Asdf123",
        is_verified=False,
    )


class TestIsOwnerAndIsVerified:

    def test_authenticated_and_verified_user_has_permission(
        self,
        rf,
        verified_user,
    ):
        permission = IsOwnerAndIsVerified()

        request = rf.get("/")
        request.user = verified_user

        assert permission.has_permission(request, None) is True

    def test_authenticated_but_unverified_user_has_no_permission(
        self,
        rf,
        unverified_user,
    ):
        permission = IsOwnerAndIsVerified()

        request = rf.get("/")
        request.user = unverified_user

        assert permission.has_permission(request, None) is False
