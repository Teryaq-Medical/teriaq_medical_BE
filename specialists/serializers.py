from rest_framework import serializers
from .models import Specialist

class SpecialistSerializer(serializers.ModelSerializer):


    class Meta:
        model = Specialist
        fields = ['id', 'name']