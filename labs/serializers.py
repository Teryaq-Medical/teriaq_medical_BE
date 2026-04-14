from rest_framework import serializers
from .models import LabSpecialists, Lab

class LabSpecialistsSerializers(serializers.ModelSerializer):
    class Meta:
        model = LabSpecialists
        fields = ['id', 'name', 'image', 'lab']
        read_only_fields = ['id']

class LabsSerializers(serializers.ModelSerializer):
    specialists = LabSpecialistsSerializers(many=True, read_only=True)
    
    class Meta:
        model = Lab
        fields = ['id', 'name', 'image', 'address', 'phone', 'email', 'rating', 'specialists', 'description']