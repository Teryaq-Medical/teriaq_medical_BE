from rest_framework.authtoken.models import Token
from .utils import set_auth_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from accounts.models import User, NormalUser, CommunityMember
from .serializers import (
    NormalUserRegisterSerializer,
    CommunityUserRegisterSerializer,
    LoginSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_normal_user(request):
    serializer = NormalUserRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = User.objects.create_user(
        email=data['email'],
        password=data['password'],
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        user_type='normal'
    )

    NormalUser.objects.create(
        user=user,
        national_id=data['national_id']
    )

    token, _ = Token.objects.get_or_create(user=user)

    response = Response(
        {
            "message": "تم تسجيل المستخدم العادي بنجاح",
            "user_type": "normal"
        },
        status=status.HTTP_201_CREATED
    )

    set_auth_cookie(response, token.key)
    return response


@api_view(['POST'])
@permission_classes([AllowAny])
def register_community_user(request):
    serializer = CommunityUserRegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = User.objects.create_user(
        email=data['email'],
        password=data['password'],
        full_name=data['full_name'],
        phone_number=data['phone_number'],
        user_type='community'
    )

    CommunityMember.objects.create(
        user=user,
        community_name=data['community_name'],
        membership_number=data['membership_number']
    )

    token, _ = Token.objects.get_or_create(user=user)

    response = Response(
        {
            "message": "تم تسجيل عضو المجتمع بنجاح",
            "user_type": "community"
        },
        status=status.HTTP_201_CREATED
    )

    set_auth_cookie(response, token.key)
    return response




@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(email=email, password=password)

    if not user:
        return Response(
            {"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"error": "هذا الحساب غير نشط"},
            status=status.HTTP_403_FORBIDDEN
        )

    token, _ = Token.objects.get_or_create(user=user)

    response = Response(
        {
            "message": "تم تسجيل الدخول بنجاح",
            "user_type": user.user_type,
            "full_name": user.full_name,
            "email":user.email,
            "phone_number":user.phone_number
        },
        status=status.HTTP_200_OK
    )

    set_auth_cookie(response,token.key)

    return response



@api_view(['POST'])
def logout(request):
    token = request.COOKIES.get('auth_token')

    if token:
        Token.objects.filter(key=token).delete()

    response = Response(
        {"message": "تم تسجيل الخروج بنجاح"},
        status=status.HTTP_200_OK
    )

    response.delete_cookie('auth_token')
    return response