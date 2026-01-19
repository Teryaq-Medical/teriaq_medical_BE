from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, CommunityMember, NormalUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'phone_number', 'user_type')



class CommunitySignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    community_name = serializers.CharField()
    membership_number = serializers.CharField()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            user_type='community'
        )

        CommunityMember.objects.create(
            user=user,
            community_name=validated_data['community_name'],
            membership_number=validated_data['membership_number']
        )

        return user

class NormalSignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
    national_id = serializers.CharField()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            user_type='normal'
        )

        NormalUser.objects.create(
            user=user,
            national_id=validated_data['national_id']
        )

        return user


