from .models import Labs,LapCategory
from rest_framework import serializers


class LabCategoriesSerializers(serializers.ModelSerializer):
    class Meta:
        model = LapCategory
        fields = '__all__'

class LabsSerializers(serializers.ModelSerializer):
    categories = LabCategoriesSerializers(many=True,read_only=True)
    
    class Meta:
        model= Labs
        fields = ['id','name','image','address','phone','email','rating','categories']