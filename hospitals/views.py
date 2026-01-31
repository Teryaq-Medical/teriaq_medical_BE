from .models import Hospital
from .serializers import HospitalSerializers
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets

class HospitalViewSet(TeriaqViewSets):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializers
    permission_classes = [IsAdminOrReadOnly]
