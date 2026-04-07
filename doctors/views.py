from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Doctor, WorkSchedule, DoctorAssignment
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from .serializers import DoctorSerializers, WorkScheduleSerializer, DoctorAssignmentSerializer
from ASER.permissions import IsAdminOrReadOnly
from ASER.viewset import TeriaqViewSets

class DoctorAssignmentViewSet(TeriaqViewSets):
    queryset = DoctorAssignment.objects.all()
    serializer_class = DoctorAssignmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    

    def get_queryset(self):
        queryset = super().get_queryset().filter(status="approved")

        h_id = self.request.query_params.get('hospital_id')
        c_id = self.request.query_params.get('clinic_id')
        l_id = self.request.query_params.get('lab_id')
        doctor_id = self.request.query_params.get('doctor_id')


        if h_id:
            ct = ContentType.objects.get_for_model(Hospital)
            return queryset.filter(
                content_type=ct,
                object_id=h_id
            )

        if c_id:
            ct = ContentType.objects.get_for_model(Clinic)
            return queryset.filter(
                content_type=ct,
                object_id=c_id
            )

        if l_id:
            ct = ContentType.objects.get_for_model(Lab)
            return queryset.filter(
                content_type=ct,
                object_id=l_id
            )

    # -------------------------
    # GLOBAL DOCTOR FILTERING
    # -------------------------

        if doctor_id:
            return queryset.filter(
                doctor_id=doctor_id,
                content_type__isnull=True,
                object_id__isnull=True
            )

        return queryset.none()


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