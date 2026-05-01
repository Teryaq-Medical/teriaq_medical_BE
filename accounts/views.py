# accounts/views.py
import logging
from django.db import transaction
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import User, CommunityMember
from .serializers import (
    NormalUserRegisterSerializer,
    CommunityUserRegisterSerializer,
    UserProfileSerializer,
    UserSerializers,
    LoginSerializer,
)
from ASER.viewset import TeriaqViewSets

logger = logging.getLogger(__name__)

# Read cookie settings from settings.py — not hardcoded
_COOKIE_SECURE   = getattr(settings, 'AUTH_COOKIE_SECURE', True)
_COOKIE_SAMESITE = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'None')


def _set_auth_cookie(response, token_key):
    response.set_cookie(
        key="auth_token",
        value=token_key,
        httponly=True,
        secure=_COOKIE_SECURE,
        samesite=_COOKIE_SAMESITE,
        path="/",
    )


class UsersViewsets(TeriaqViewSets):
    queryset = User.objects.all()
    serializer_class = UserSerializers
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_type']


class AuthViewSet(TeriaqViewSets):
    """
    Replaces all the @api_view functions with a single class-based viewset.
    Responses go through the TeriaqViewSets envelope automatically.
    """
    serializer_class = UserSerializers   # default; overridden per action

    def get_permissions(self):
        if self.action in ['register_normal', 'register_community', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='register/normal')
    @transaction.atomic
    def register_normal(self, request):
        if request.data.get("password") != request.data.get("confirm_password"):
            return Response(
                {"status": "error", "message": "كلمات المرور غير متطابقة"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = NormalUserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        response = Response(
            {"status": "success",
             "message": {"en": "Registered successfully", "ar": "تم التسجيل بنجاح"},
             "data": {"user_type": user.user_type}},
            status=status.HTTP_201_CREATED
        )
        _set_auth_cookie(response, token.key)
        return response

    @action(detail=False, methods=['post'], url_path='register/community')
    @transaction.atomic
    def register_community(self, request):
        if request.data.get("password") != request.data.get("confirm_password"):
            return Response(
                {"status": "error", "message": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = CommunityUserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        response = Response(
            {"status": "success",
             "message": {"en": "Registered successfully", "ar": "تم التسجيل بنجاح"},
             "data": {"user_type": user.user_type}},
            status=status.HTTP_201_CREATED
        )
        _set_auth_cookie(response, token.key)
        return response

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response(
                {"status": "error", "message": {"en": "Invalid credentials", "ar": "بيانات غير صحيحة"}},
                status=status.HTTP_401_UNAUTHORIZED
            )
        token, _ = Token.objects.get_or_create(user=user)
        response = Response({
            "status": "success",
            "message": {"en": "Login successful", "ar": "تم تسجيل الدخول"},
            "data": {}
        })
        _set_auth_cookie(response, token.key)
        return response

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()
        response = Response({
            "status": "success",
            "message": {"en": "Logged out", "ar": "تم تسجيل الخروج"},
            "data": {}
        })
        response.delete_cookie("auth_token")
        return response

    @action(detail=False, methods=['get'], url_path='profile')
    def profile(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response({
            "status": "success",
            "message": {"en": "Profile retrieved", "ar": "تم جلب الملف الشخصي"},
            "data": serializer.data
        })