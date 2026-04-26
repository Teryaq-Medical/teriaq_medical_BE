import logging
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser,SAFE_METHODS
from django.contrib.contenttypes.models import ContentType

from .models import Doctor, WorkSchedule, DoctorAssignment, UnregisteredDoctor
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from .serializers import (
    DoctorSerializers,
    WorkScheduleSerializer,
    DoctorAssignmentSerializer,
    UnregisteredDoctorSerializer,
    DoctorAssignmentStatusUpdateSerializer,   # NEW
)
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets

logger = logging.getLogger(__name__)


class DoctorAssignmentViewSet(viewsets.ModelViewSet):
    queryset = DoctorAssignment.objects.all()
    serializer_class = DoctorAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Ensure only admins can perform update/delete actions on assignments.
        """
        if self.action in ['update', 'partial_update', 'destroy', 'update_status']:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        doctor_id = self.request.query_params.get('doctor_id')

        if user.is_staff or user.is_superuser:
            qs = DoctorAssignment.objects.all()
        else:
            qs = DoctorAssignment.objects.filter(status="approved")
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

        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)

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

        assignments = DoctorAssignment.objects.filter(doctor_id=doctor_id, status="approved")
        schedules = WorkSchedule.objects.filter(assignment__in=assignments).select_related('assignment')
        serializer = WorkScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='update-status')
    def update_status(self, request):
        """
        Endpoint to update the status of a specific DoctorAssignment.
        Expected payload:
        {
            "assignment_id": 123,
            "status": "approved"  # or "pending", "rejected", "inactive"
        }
        """
        assignment_id = request.data.get('assignment_id')
        new_status = request.data.get('status')

        if not assignment_id:
            return Response({"error": "assignment_id is required"}, status=400)
        if new_status not in dict(DoctorAssignment.STATUS_CHOICES):
            return Response({"error": f"Invalid status. Choices: {list(dict(DoctorAssignment.STATUS_CHOICES).keys())}"}, status=400)

        try:
            assignment = DoctorAssignment.objects.get(id=assignment_id)
        except DoctorAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=404)

        assignment.status = new_status
        assignment.save()

        # Return the updated assignment data
        serializer = DoctorAssignmentSerializer(assignment)
        return Response(serializer.data)


class WorkScheduleViewSet(TeriaqViewSets):
    queryset = WorkSchedule.objects.all()
    serializer_class = WorkScheduleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        assignment_id = self.request.query_params.get('assignment')
        doctor_id = self.request.query_params.get('doctor_id')

        if assignment_id:
            return queryset.filter(assignment_id=assignment_id)
        if doctor_id:
            return queryset.filter(
                assignment__doctor_id=doctor_id,
                assignment__entity_type="individual"
            )
        return queryset

    def perform_create(self, serializer):
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
    queryset = UnregisteredDoctor.objects.prefetch_related(
        'assignments__content_type'
    ).all()
    serializer_class = UnregisteredDoctorSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method in SAFE_METHODS:
            return
        if request.user.is_staff or request.user.is_superuser:
            return
        if hasattr(request.user, 'user_type') and request.user.user_type in ['hospitals', 'clincs', 'labs']:
            if request.user.user_type == 'hospitals':
                entity = Hospital.objects.filter(user=request.user).first()
            elif request.user.user_type == 'clincs':
                entity = Clinic.objects.filter(user=request.user).first()
            elif request.user.user_type == 'labs':
                entity = Lab.objects.filter(user=request.user).first()
            else:
                entity = None
            if entity:
                content_type = ContentType.objects.get_for_model(entity)
                if DoctorAssignment.objects.filter(
                    content_type=content_type,
                    object_id=entity.id,
                    unregistered_doctor=obj,
                    status='approved'
                ).exists():
                    return
        self.permission_denied(request)

    # 🔧 Override to guarantee allow_online_booking is saved
    def perform_update(self, serializer):
        # Log the request data
        logger.info(f"PATCH data: {self.request.data}")
        
        # If allow_online_booking is in the request, force it
        if 'allow_online_booking' in self.request.data:
            serializer.save(allow_online_booking=self.request.data.get('allow_online_booking'))
        else:
            serializer.save()