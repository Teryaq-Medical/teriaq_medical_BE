from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import Lab, LabSpecialists
from .serializers import LabsSerializers, LabSpecialistsSerializers
from ASER.permissions import IsAdminOrMedicalEntity, IsLabOwnerOrAdmin

class LabsViewSets(viewsets.ModelViewSet):
    queryset = Lab.objects.all()
    serializer_class = LabsSerializers
    permission_classes = [IsAdminOrMedicalEntity]

class LabSpecialistsViewSet(viewsets.ModelViewSet):
    queryset = LabSpecialists.objects.all()
    serializer_class = LabSpecialistsSerializers
    permission_classes = [IsLabOwnerOrAdmin]

    def perform_create(self, serializer):
        lab_id = self.request.data.get('lab')
        if not lab_id:
            raise ValidationError({"lab": "Lab ID is required"})
        try:
            lab = Lab.objects.get(id=lab_id)
        except Lab.DoesNotExist:
            raise ValidationError({"lab": "Lab not found"})
        # Check permission
        if not (self.request.user.is_staff or lab.user == self.request.user):
            raise PermissionDenied("You do not have permission to add specialists to this lab.")
        serializer.save(lab=lab)  # explicitly set lab