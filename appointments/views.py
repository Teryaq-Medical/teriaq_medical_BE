# appointments/views.py
import logging
from django.db import transaction, IntegrityError
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Appointment, LabBooking
from .serializers import AppointmentSerializer, LabBookingSerializer
from doctors.models import DoctorAssignment
from hospitals.models import Hospital
from clincs.models import Clinic
from doctors.models import Doctor
from labs.models import Lab
from ASER.viewset import TeriaqViewSets
from ASER.utils import get_entity_for_user   # ← replaces the copy-paste blocks

logger = logging.getLogger(__name__)


class AppointmentViewSet(TeriaqViewSets):     # ← was ModelViewSet
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Appointment.objects.all()\
                .select_related('patient', 'assignment').order_by("-created_at")

        if user.user_type == "normal":
            return Appointment.objects.filter(patient=user)\
                .select_related('patient', 'assignment').order_by("-created_at")

        if user.user_type in ["hospitals", "clincs", "doctors", "labs"]:
            entity, _ = get_entity_for_user(user)   # ← replaces 20-line if block
            if not entity:
                return Appointment.objects.none()

            if user.user_type == "doctors":
                assignments = DoctorAssignment.objects.filter(
                    Q(doctor=entity) |
                    Q(content_type=ContentType.objects.get_for_model(entity),
                      object_id=entity.id)
                )
            else:
                content_type = ContentType.objects.get_for_model(entity)
                assignments = DoctorAssignment.objects.filter(
                    content_type=content_type, object_id=entity.id
                )
            return Appointment.objects.filter(assignment__in=assignments)\
                .select_related('patient', 'assignment').order_by("-created_at")

        return Appointment.objects.none()

    # No create() override needed — TeriaqViewSets.create handles it
    # perform_create sets the patient from the request user
    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        new_status = request.data.get('status')
        booking_code = request.data.get('booking_code')

        if new_status == 'completed':
            if not booking_code:
                return Response({"error": "Booking code required"}, status=400)
            if instance.booking_code != booking_code:
                return Response({"error": "Invalid booking code"}, status=400)
            instance.status = 'completed'
            instance.save()
            return Response(self.get_serializer(instance).data)

        if new_status:
            allowed = ['confirmed', 'cancelled', 'no_show']
            if new_status not in allowed:
                return Response({"error": f"Invalid status. Allowed: {allowed}"}, status=400)
            instance.status = new_status
            instance.save()
            return Response(self.get_serializer(instance).data)

        return super().partial_update(request, *args, **kwargs)


class LabBookingViewSet(TeriaqViewSets):    # ← was ModelViewSet
    serializer_class = LabBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        lab_id = self.request.query_params.get('lab')

        if user.is_staff:
            qs = LabBooking.objects.all()
            if lab_id:
                qs = qs.filter(lab_id=lab_id)
            return qs.select_related('patient').order_by("-created_at")

        try:
            lab = Lab.objects.get(user=user)
            qs = LabBooking.objects.filter(lab=lab)
        except Lab.DoesNotExist:
            qs = LabBooking.objects.filter(patient=user)

        if lab_id:
            qs = qs.filter(lab_id=lab_id)
        return qs.select_related('patient').order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        if 'status' not in request.data:
            return Response({"error": "Only status updates are allowed"}, status=400)
        new_status = request.data['status']
        if new_status == 'completed' and 'booking_code' in request.data:
            if booking.booking_code != request.data['booking_code']:
                return Response({"error": "Invalid booking code"}, status=400)
        booking.status = new_status
        booking.save()
        return Response(self.get_serializer(booking).data)