from rest_framework import serializers
from .models import Doctors
from specialists.serializers import SpecialistSerializer

class DoctorSerializers(serializers.ModelSerializer):
    specialist = SpecialistSerializer(read_only=True)
    class Meta:
        model = Doctors
        fields = ['id','name','age','doctor_image','phone_number','address','specialist']
        
    