from rest_framework import serializers
from .models import Clinic
from specialists.serializers import SpecialistSerializer


class ClincsSerializer(serializers.ModelSerializer):
    specialists = SpecialistSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'address', 'phone', 'email', 'description',
            'image', 'image_url', 'rating', 'specialists', 'insurance', 'certificates', 'about'
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url if hasattr(obj.image, 'url') else obj.image
        return None