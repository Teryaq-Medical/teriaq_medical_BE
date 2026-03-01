from rest_framework import serializers
from accounts.models import User, NormalUser, CommunityMember



class UserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class BaseRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'}
    )
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=20)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل")
        return value

    def create_user(self, validated_data, user_type):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=validated_data["email"],
            password=password,
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            user_type=user_type
        )
        return user


class NormalUserRegisterSerializer(BaseRegisterSerializer):
    national_id = serializers.CharField(max_length=50)

    def validate_national_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("الرقم القومي يجب أن يحتوي على أرقام فقط")
        return value

    def create(self, validated_data):
        national_id = validated_data.pop("national_id")

        user = self.create_user(validated_data, user_type="normal")

        NormalUser.objects.create(
            user=user,
            national_id=national_id
        )

        return user


class CommunityUserRegisterSerializer(BaseRegisterSerializer):
    community_name = serializers.CharField(max_length=255)
    membership_number = serializers.CharField(max_length=100)

    def create(self, validated_data):
        community_name = validated_data.pop("community_name")
        membership_number = validated_data.pop("membership_number")

        user = self.create_user(validated_data, user_type="community")

        CommunityMember.objects.create(
            user=user,
            community_name=community_name,
            membership_number=membership_number
        )

        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

class UserProfileSerializer(serializers.ModelSerializer):
    # These fields match the 'source' keys in your TypeScript FieldConfig
    normal_profile = serializers.SerializerMethodField()
    community_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number', 'user_type', 'normal_profile', 'community_profile']

    def get_normal_profile(self, obj):
        if obj.user_type == "normal" and hasattr(obj, 'normal_profile'):
            return {"national_id": obj.normal_profile.national_id}
        return None

    def get_community_profile(self, obj):
        if obj.user_type == "community" and hasattr(obj, 'community_profile'):
            return {
                "community_name": obj.community_profile.community_name,
                "membership_number": obj.community_profile.membership_number
            }
        return None