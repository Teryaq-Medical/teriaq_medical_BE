from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from accounts.models import User, NormalUser,CommunityMember
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


@api_view(['POST'])
def register_normal(request):
    data = request.data

    if data.get("password") != data.get("confirm_password"):
        return Response({"detail": "Passwords do not match"}, status=400)

    user = User.objects.create(
        email=data["email"],
        full_name=data["full_name"],
        phone_number=data["phone_number"],
        user_type="normal",
        password=make_password(data["password"]),
    )

    NormalUser.objects.create(
        user=user,
        national_id=data["national_id"]
    )

    token = Token.objects.create(user=user)

    response = Response(
        {"message": "Registered successfully"},
        status=status.HTTP_201_CREATED
    )

    response.set_cookie(
        key="auth_token",
        value=token.key,
        httponly=True,
        secure=False,   # True in production
        samesite="Lax",
    )

    return response


@api_view(['POST'])
def register_community(request):
    data = request.data

    if data.get("password") != data.get("confirm_password"):
        return Response({"detail": "Passwords do not match"}, status=400)

    user = User.objects.create(
        email=data["email"],
        full_name=data["full_name"],
        phone_number=data["phone_number"],
        user_type="community",
        password=make_password(data["password"]),
    )

    CommunityMember.objects.create(
        user=user,
        community_name=data["community_name"],
        membership_number=data["membership_number"]
    )

    token = Token.objects.create(user=user)

    response = Response(
        {"message": "Registered successfully"},
        status=status.HTTP_201_CREATED
    )

    response.set_cookie(
        key="auth_token",
        value=token.key,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    return response


@api_view(['POST'])
def login_view(request):
    user = authenticate(
        email=request.data.get("email"),
        password=request.data.get("password")
    )

    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)

    response = Response({"message": "Login successful"})

    response.set_cookie(
        key="auth_token",
        value=token.key,
        httponly=True,
        secure=False,
        samesite="Lax",
    )

    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()

    response = Response({"message": "Logged out"})
    response.delete_cookie("auth_token")

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user

    if user.user_type == "normal":
        profile_data = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "national_id": user.normal_profile.national_id,
        }

    elif user.user_type == "community":
        profile_data = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "community_name": user.community_profile.community_name,
            "membership_number": user.community_profile.membership_number,
        }

    else:
        profile_data = {
            "full_name": user.full_name,
            "email": user.email,
            "phone_number": user.phone_number,
        }

    return Response({
        "user_type": user.user_type,
        "profile": profile_data
    })