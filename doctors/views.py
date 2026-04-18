from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Doctor, WorkSchedule, DoctorAssignment,UnregisteredDoctor
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from .serializers import DoctorSerializers, WorkScheduleSerializer, DoctorAssignmentSerializer,UnregisteredDoctorSerializer
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets

from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import WorkScheduleSerializer
from rest_framework import viewsets
class DoctorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DoctorAssignment.objects.all()
    serializer_class = DoctorAssignmentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        doctor_id = self.request.query_params.get('doctor_id')
        
        # Start with approved assignments
        qs = DoctorAssignment.objects.filter(status="approved")
        
        # If user is admin → return everything (including pending)
        if user.is_staff or user.is_superuser:
            qs = DoctorAssignment.objects.all()
        else:
            # Check if user is an entity owner (hospital, clinic, lab)
            entity_type = user.user_type
            if entity_type in ["hospitals", "clincs", "labs"]:
                # Get the user's entity
                if entity_type == "hospitals":
                    from hospitals.models import Hospital
                    entity = Hospital.objects.get(user=user)
                elif entity_type == "clincs":
                    from clincs.models import Clinic
                    entity = Clinic.objects.get(user=user)
                elif entity_type == "labs":
                    from labs.models import Lab
                    entity = Lab.objects.get(user=user)
                else:
                    entity = None
                
                if entity:
                    content_type = ContentType.objects.get_for_model(entity)
                    # Include both approved AND pending for this entity
                    qs = DoctorAssignment.objects.filter(
                        content_type=content_type,
                        object_id=entity.id
                    )
        
        # Apply doctor_id filter (if provided)
        if doctor_id:
            if not (user.is_staff or user.is_superuser):
                # Non‑admin can only see their own doctor profile
                try:
                    doctor = Doctor.objects.get(user=user)
                    if int(doctor_id) != doctor.id:
                        return DoctorAssignment.objects.none()
                except Doctor.DoesNotExist:
                    return DoctorAssignment.objects.none()
            qs = qs.filter(doctor_id=doctor_id)
        
        # Apply entity filters (hospital_id, clinic_id, lab_id)
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
        
        return qs

    @action(detail=False, methods=['get'], url_path='schedules')
    def get_doctor_schedules(self, request):
        doctor_id = request.query_params.get('doctor_id')
        if not doctor_id:
            return Response({"error": "doctor_id is required"}, status=400)

        user = request.user
        
        # Permission check: only admin or the doctor themselves can view
        if not (user.is_staff or user.is_superuser):
            try:
                doctor = Doctor.objects.get(user=user)
                if int(doctor_id) != doctor.id:
                    return Response({"error": "Permission denied"}, status=403)
            except Doctor.DoesNotExist:
                return Response({"error": "Doctor not found"}, status=404)

        # Personal (global) assignments
        personal_assignments = DoctorAssignment.objects.filter(
            doctor_id=doctor_id,
            content_type__isnull=True,
            object_id__isnull=True,
            status="approved"
        )
        # Entity assignments
        entity_assignments = DoctorAssignment.objects.filter(
            doctor_id=doctor_id,
            content_type__isnull=False,
            status="approved"
        )
        assignments = personal_assignments | entity_assignments
        schedules = WorkSchedule.objects.filter(assignment__in=assignments).select_related('assignment')
        serializer = WorkScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

class WorkScheduleViewSet(TeriaqViewSets):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Important: Filter schedules by the assignment link
        assignment_id = self.request.query_params.get('assignment')
        if assignment_id:
            return queryset.filter(assignment_id=assignment_id)
        return queryset
    def save(self, *args, **kwargs):
        if self.start_time:
            self.start_time = self.start_time.replace(second=0, microsecond=0)

        if self.end_time:
            self.end_time = self.end_time.replace(second=0, microsecond=0)

        super().save(*args, **kwargs)


class DoctorsViewSet(TeriaqViewSets):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializers
    permission_classes = [IsAdminOrReadOnly]

class UnregisteredDoctorsViewSet(TeriaqViewSets):
    queryset = UnregisteredDoctor.objects.all()
    serializer_class = UnregisteredDoctorSerializer
    permission_classes = [IsAdminOrReadOnly]
    
