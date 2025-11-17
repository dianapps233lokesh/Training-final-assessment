from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from activity_logs.utils import log_activity
from authentication.serializers import (
    LoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(
            user=user,
            action="user_registered",
            entity_type="user",
            entity_id=user.id,
            details={"username": user.username, "email": user.email},
            request=request,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        if user:
            refresh = RefreshToken.for_user(user)
            log_activity(
                user=user,
                action="user_logged_in",
                entity_type="user",
                entity_id=user.id,
                details={"username": user.username},
                request=request,
            )
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_200_OK,
            )
        log_activity(
            action="failed_login_attempt",
            details={"username": serializer.validated_data["username"]},
            request=request,
        )
        return Response(
            {"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_activity(
            user=request.user,
            action="user_profile_updated",
            entity_type="user",
            entity_id=request.user.id,
            details=serializer.data,
            request=request,
        )
        return Response(serializer.data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_activity(
                user=request.user,
                action="user_logged_out",
                entity_type="user",
                entity_id=request.user.id,
                request=request,
            )
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            log_activity(
                user=request.user,
                action="failed_logout_attempt",
                entity_type="user",
                entity_id=request.user.id,
                request=request,
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)
