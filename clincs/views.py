from django.shortcuts import render
from .serializers import ClincsSerializer
from .models import Clincs
from ASER.viewset import TeriaqViewSets
from rest_framework.permissions import IsAdminUser
from ASER.permissions import IsAdminOrReadOnly



class ClincsViewSet(TeriaqViewSets):
    serializer_class = ClincsSerializer
    queryset = Clincs.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    

