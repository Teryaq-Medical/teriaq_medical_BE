import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import IsAuthenticated

from .models import Doctor, WorkSchedule, DoctorAssignment, UnregisteredDoctor
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from .serializers import (
    DoctorSerializers,
    WorkScheduleSerializer,
    DoctorAssignmentSerializer,
    UnregisteredDoctorSerializer,
)
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets

logger = logging.getLogger(__name__)


from rest_framework.permissions import IsAuthenticated

class DoctorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DoctorAssignment.objects.all()
    serializer_class = DoctorAssignmentSerializer
    permission_classes = [IsAuthenticated]  # ✅ Change to IsAuthenticated

    def get_queryset(self):
        user = self.request.user
        doctor_id = self.request.query_params.get('doctor_id')

        # Base queryset
        if user.is_staff or user.is_superuser:
            qs = DoctorAssignment.objects.all()
        else:
            qs = DoctorAssignment.objects.filter(status="approved")

            # If user is an entity owner, also include pending for their own entity
            entity_type = user.user_type
            if entity_type in ["hospitals", "clincs", "labs"]:
                if entity_type == "hospitals":
                    entity = Hospital.objects.get(user=user)
                elif entity_type == "clincs":
                    entity = Clinic.objects.get(user=user)
                elif entity_type == "labs":
                    entity = Lab.objects.get(user=user)
                else:
                    entity = None

                if entity:
                    content_type = ContentType.objects.get_for_model(entity)
                    qs = DoctorAssignment.objects.filter(
                        content_type=content_type,
                        object_id=entity.id
                    )

        # Filter by doctor_id – public for all authenticated users
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

        # Entity filters
        h_id = self.request.query_params.get('hospital_id')
        c_id = self.request.query_params.get('clinic_id')
        l_id = self.request.query_params.get('lab_id')
        if h_id:
            ct = ContentType.objects.get_for_model(Hospital)
            qs = qs.filter(content_type=ct, object_id=h_id)
        if c_id:
            ct = ContentType.objects.get_for_model(Clinic)
            qs = qs.filter(content_type=ct, object_id=c_id)
        if l_id:
            ct = ContentType.objects.get_for_model(Lab)
            qs = qs.filter(content_type=ct, object_id=l_id)

        return qs.select_related('doctor', 'unregistered_doctor')

    @action(detail=False, methods=['get'], url_path='schedules')
    def get_doctor_schedules(self, request):
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=400)

        # Any authenticated user can see approved schedules
        assignments = DoctorAssignment.objects.filter(doctor_id=doctor_id, status="approved")
        schedules = WorkSchedule.objects.filter(assignment__in=assignments).select_related('assignment')
        serializer = WorkScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class WorkScheduleViewSet(TeriaqViewSets):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        assignment_id = self.request.query_params.get('assignment')
        doctor_id = self.request.query_params.get('doctor_id')

        # Priority 1: Filter by specific Assignment ID
        if assignment_id:
            return queryset.filter(assignment_id=assignment_id)
        
        # Priority 2: Filter by Doctor ID (Look for their 'individual' assignment)
        if doctor_id:
            return queryset.filter(
                assignment__doctor_id=doctor_id, 
                assignment__entity_type="individual"
            )
            
        return queryset

    def perform_create(self, serializer):
        # ... (keep your existing time stripping logic)
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')
        if start_time:
            start_time = start_time.replace(second=0, microsecond=0)
        if end_time:
            end_time = end_time.replace(second=0, microsecond=0)
        serializer.save(start_time=start_time, end_time=end_time)


class DoctorsViewSet(TeriaqViewSets):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializers
    permission_classes = [IsAdminOrReadOnly]


class UnregisteredDoctorsViewSet(TeriaqViewSets):
    queryset = UnregisteredDoctor.objects.all()
    serializer_class = UnregisteredDoctorSerializer
    permission_classes = [IsAdminOrReadOnly]