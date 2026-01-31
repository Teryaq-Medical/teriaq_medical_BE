from django.shortcuts import render
from .models import Doctors
from .serializers import DoctorSerializers
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets


class DoctorsViewSet(TeriaqViewSets):
    queryset = Doctors.objects.all()
    serializer_class = DoctorSerializers
    permission_classes = [IsAdminOrReadOnly]
    
