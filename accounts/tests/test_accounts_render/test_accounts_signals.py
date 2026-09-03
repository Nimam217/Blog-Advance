'''import pytest

from accounts.models import Profile, User
from rest_framework.authtoken.models import Token


@pytest.mark.django_db
class TestUserSignals:

    def test_profile_created_automatically(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        profile = Profile.objects.get(user=user)

        assert profile.user == user

    def test_token_created_automatically(self):
        user = User.objects.create_user(
            email="test@gmail.com",
            password="@Asdf123",
        )

        token = Token.objects.get(user=user)

        assert token.user == user
        assert token.key'''