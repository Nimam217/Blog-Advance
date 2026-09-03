from django.contrib.auth import authenticate
from django.core import exceptions
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from accounts.models import User, Profile


class RegisterViewSerializer(serializers.ModelSerializer):
    password_confirmation = serializers.CharField(
        max_length=255, write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "password", "password_confirmation"]

    def validate(self, data):

        if data.get("password") != data.get("password_confirmation"):
            raise serializers.ValidationError(
                {"detail": "Passwords must match"}
            )
        try:
            validate_password(data.get("password"))

        except exceptions.ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return super().validate(data)

    def create(self, validated_data):

        validated_data.pop("password_confirmation")
        return User.objects.create_user(**validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"), write_only=True)
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label=_("Token"), read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"),
                email=email,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Unable to log in with provided credentials.")
                raise serializers.ValidationError(msg, code="authorization")

            if not user.is_verified:
                raise serializers.ValidationError(
                    {"detail": "user not verified"}
                )

        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


class CustomJwtTokenPairViewSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError({"detail": "user not verified"})
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
        }

        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)

    new_password = serializers.CharField(required=True, write_only=True)

    new_password_confirmation = serializers.CharField(
        required=True, write_only=True
    )

    def validate(self, data):
        if data["new_password"] != data["new_password_confirmation"]:
            raise serializers.ValidationError(
                {"new_password_confirmation": "Passwords must match."}
            )

        try:
            validate_password(
                data["new_password"], self.context["request"].user
            )
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password": list(e.messages)}
            )

        return super().validate(data)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "email", "first_name", "last_name", "description"]


class ResendActivationSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def validate(self, data):

        email = data.get("email")
        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "User does not exist"}
            )

        data["user"] = user

        return super().validate(data)


class ResetPasswordEmaiSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)

    def validate(self, data):
        email = data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "User does not exist"}
            )

        data["user"] = user
        return super().validate(data)


class ResetPasswordViewSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True)
    new_password_confirmation = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["new_password", "new_password_confirmation"]

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirmation"]:
            raise serializers.ValidationError(
                {"new_password_confirmation": "Passwords must match"}
            )
        try:
            validate_password(attrs["new_password"])
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"new_password_confirmation": list(e.messages)}
            )

        return super().validate(attrs)
