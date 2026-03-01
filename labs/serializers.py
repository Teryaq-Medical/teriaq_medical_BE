from .models import Lab
from rest_framework import serializers
from specialists.serializers import SpecialistSerializer



class LabsSerializers(serializers.ModelSerializer):
    specialists = SpecialistSerializer(many=True,read_only=True)
    
    class Meta:
        model= Lab
        fields = ['id','name','image','address','phone','email','rating','specialists']