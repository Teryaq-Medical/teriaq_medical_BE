from rest_framework import serializers


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
        from accounts.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل")
        return value



class NormalUserRegisterSerializer(BaseRegisterSerializer):
    national_id = serializers.CharField(max_length=50)

    def validate_national_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("الرقم القومي يجب أن يحتوي على أرقام فقط")
        return value


class CommunityUserRegisterSerializer(BaseRegisterSerializer):
    community_name = serializers.CharField(max_length=255)
    membership_number = serializers.CharField(max_length=100)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
