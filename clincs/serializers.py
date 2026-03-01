from rest_framework import serializers
from .models import Clinic
from specialists.serializers import SpecialistSerializer


class ClincsSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    Specialist = SpecialistSerializer(many=True, read_only=True)
    

    class Meta:
        model = Clinic
        fields = ['id', 'name', 'image_url','Specialist']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None