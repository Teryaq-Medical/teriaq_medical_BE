from .models import Hospital
from rest_framework import serializers
from specialists.serializers import SpecialistSerializer

class HospitalSerializers(serializers.ModelSerializer):
    specialist = SpecialistSerializer(many=True,read_only=True)
    class Meta:
        model= Hospital
        fields = ['id','name','image','address','phone','email','rating','specialist']