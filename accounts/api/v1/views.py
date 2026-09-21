from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from accounts.models import Profile, User
from accounts.api.v1.serializers import (
    RegisterViewSerializer,
    CustomAuthTokenSerializer,
    CustomJwtTokenPairViewSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ResendActivationSerializer,
    ResetPasswordViewSerializer,
    ResetPasswordEmailSerializer,
)
from rest_framework_simplejwt.tokens import AccessToken

from rest_framework_simplejwt.exceptions import AuthenticationFailed
import jwt
from core import settings
from .permissions import IsOwnerAndIsVerified
from ...tasks import (
    send_email_reset_password,
    send_email_resend_activation_email,
    send_email_register_activation,
)


class RegisterView(generics.GenericAPIView):

    serializer_class = RegisterViewSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            user = get_object_or_404(User, email=email)
            access = AccessToken.for_user(user)
            token = str(access)

            send_email_register_activation.apply_async(
                args=[token, user.id],
                expires=60,
                retry=True,
                retry_policy={
                    "max_retries": 3,
                    "interval_start": 1,
                    "interval_step": 2,
                    "interval_max": 10,
                },
            )
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email}
        )


class CustomDiscardAuthToken(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomJwtTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomJwtTokenPairViewSerializer


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    permission_classes = (IsOwnerAndIsVerified,)
    serializer_class = ProfileSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class ActivationView(APIView):
    def get(
        self,
        request,
        token,
        *args,
        **kwargs,
    ):

        try:
            token = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = token.get("user_id")
            user = get_object_or_404(User, pk=user_id)

        except jwt.ExpiredSignatureError:

            return Response(
                {"detail": "link expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:

            return Response(
                {"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
        if not user.is_verified:
            user.is_verified = True
            user.save()
            return Response(
                {"detail": "successfully activated"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "user have been already verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ResendActivationEmail(generics.GenericAPIView):
    serializer_class = ResendActivationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data["email"],
            is_verified=False,
        ).first()

        if user:
            access = AccessToken.for_user(user)
            token = str(access)
            send_email_resend_activation_email.apply_async(
                args=[token, user.id],
                expires=60,
                retry=True,
                retry_policy={
                    "max_retries": 3,
                    "interval_start": 1,
                    "interval_step": 2,
                    "interval_max": 10,
                },
            )

        return Response(
            {
                "detail": "If the account exists and is not verified, "
                "an activation email has been sent.",
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email=serializer.validated_data["email"],
            is_verified=True,
        ).first()

        if user:
            access = AccessToken.for_user(user)
            token = str(access)
            send_email_reset_password.apply_async(
                args=[token, user.id],
                expires=60,
                retry=True,
                retry_policy={
                    "max_retries": 3,
                    "interval_start": 1,
                    "interval_step": 2,
                    "interval_max": 10,
                },
            )

        return Response(
            {
                "detail": "If your account exists and is verified, "
                "an email has been sent successfully.",
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordViewSerializer

    def post(
        self,
        request,
        token,
        *args,
        **kwargs,
    ):
        serializer = self.get_serializer(data=request.data)

        try:
            decoded_token = jwt.decode(
                jwt=token, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = get_object_or_404(User, pk=decoded_token["user_id"])
            if not user.is_verified:
                raise AuthenticationFailed("User is not verified")

            elif user.is_verified:
                serializer.is_valid(raise_exception=True)
                new_password = serializer.validated_data["new_password"]
                user.set_password(new_password)
                user.save()
                return Response(
                    {"detail": "password has been reset successfully"},
                    status=status.HTTP_200_OK,
                )

        except jwt.ExpiredSignatureError:
            return Response(
                {"detail": "link expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.InvalidTokenError:
            return Response(
                {"detail": "invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )
