from rest_framework import serializers
from .models import Insurance, Certifications, Biography


from rest_framework import serializers
from .models import Insurance

class InsuranceSerializer(serializers.ModelSerializer):
    status_display_ar = serializers.SerializerMethodField()

    class Meta:
        model = Insurance
        fields = ['id', 'entity', 'status', 'status_display_ar']

    def get_status_display_ar(self, obj):
        # Map English DB values to Arabic
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
        fields = [
            'id',
            'name',
            'entity',
        ]


class BiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = [
            'id',
            'bio',
            'bio_details',
            'experiance',
            'operaiton',
        ]
