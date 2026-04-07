# ASER/serializers.py

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


# Write Serializers for Update Operations
class InsuranceWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ['entity', 'status']


class CertificationsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = ['name', 'entity']


class BiographyWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = ['bio', 'bio_details', 'experiance', 'operaiton']