from rest_framework import serializers
from .models import Insurance, Certifications, Biography


class InsuranceSerializer(serializers.ModelSerializer):
    status_display_ar = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Insurance
        fields = ['id', 'entity', 'status', 'status_display_ar']

    def get_status_display_ar(self, obj):
        mapping = {
            'full': 'تغطية كاملة',
            'standard': 'عادية',
            'partial': 'جزئية',
            'expired': 'منتهية'
        }
        return mapping.get(obj.status.lower(), obj.status)


class CertificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = ['id', 'name', 'entity']


class BiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = ['id', 'bio', 'bio_details', 'experiance', 'operaiton']

class InsuranceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['entity', 'status']

    def validate_status(self, value):
        valid_choices = ['تغطية كاملة', 'عادية', 'جزئية', 'منتهية']
        mapping = {
            'active': 'عادية',
            'full': 'تغطية كاملة',
            'standard': 'عادية',
            'partial': 'جزئية',
            'expired': 'منتهية'
        }
        if value in mapping:
            return mapping[value]
        if value in valid_choices:
            return value
        raise serializers.ValidationError(
            f"Invalid status. Use one of: {valid_choices} or active/full/standard/partial/expired"
        )


class CertificationsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = ['name', 'entity']


class BiographyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = ['bio', 'bio_details', 'experiance', 'operaiton']
        extra_kwargs = {
            'bio': {'required': False, 'allow_blank': True},
            'bio_details': {'required': False, 'allow_blank': True},
            'experiance': {'required': False},
            'operaiton': {'required': False},
        }