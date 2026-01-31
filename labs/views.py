from django.shortcuts import render
from .models import Labs
from .serializers import LabsSerializers
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets


class LabsViewSets(TeriaqViewSets):
    queryset = Labs.objects.all()
    serializer_class = LabsSerializers
    permission_classes = [IsAdminOrReadOnly]

 