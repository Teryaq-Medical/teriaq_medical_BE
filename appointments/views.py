import logging
from django.db import transaction, IntegrityError
from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment, LabBooking
from .serializers import AppointmentSerializer, LabBookingSerializer

logger = logging.getLogger(__name__)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        print(user.user_type)
        
        if user.is_staff:
            return Appointment.objects.all().select_related('patient', 'assignment').order_by("-created_at")
        
        if user.user_type == "normal":
            return Appointment.objects.filter(patient=user).select_related('patient', 'assignment').order_by("-created_at")
        
        # For entity owners (hospitals, clinics, doctors, labs)
        if user.user_type in ["hospitals", "clincs", "doctors", "labs"]:
            from django.contrib.contenttypes.models import ContentType
            from doctors.models import DoctorAssignment
            
            # Get the entity based on user_type
            if user.user_type == "hospitals":
                from hospitals.models import Hospital
                entity = Hospital.objects.get(user=user)
            elif user.user_type == "clincs":
                from clincs.models import Clinic
                entity = Clinic.objects.get(user=user)
            elif user.user_type == "doctors":
                from doctors.models import Doctor
                entity = Doctor.objects.get(user=user)
            elif user.user_type == "labs":
                from labs.models import Lab
                entity = Lab.objects.get(user=user)
            else:
                return Appointment.objects.none()
            
            # Build queryset of assignments
            if user.user_type == "doctors":
                # For doctors: include both personal assignments (doctor=entity) 
                # and entity-linked assignments (via content_type)
                assignments = DoctorAssignment.objects.filter(
                    Q(doctor=entity) | 
                    Q(content_type=ContentType.objects.get_for_model(entity), object_id=entity.id)
                )
            else:
                # For hospitals/clinics/labs: only entity-linked assignments
                content_type = ContentType.objects.get_for_model(entity)
                assignments = DoctorAssignment.objects.filter(
                    content_type=content_type,
                    object_id=entity.id
                )
            
            return Appointment.objects.filter(assignment__in=assignments).select_related('patient', 'assignment').order_by("-created_at")
        
        return Appointment.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        logger.info("========== APPOINTMENT CREATE START ==========")
        logger.info(f"User: {request.user}")
        logger.info(f"Payload: {request.data}")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=400)

        try:
            self.perform_create(serializer)
        except IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            return Response({"detail": "Database integrity error"}, status=400)
        except Exception as e:
            logger.exception("Unexpected error")
            return Response({"detail": "Unexpected server error"}, status=500)

        return Response(serializer.data, status=201)

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
        elif new_status:
            allowed = ['confirmed', 'cancelled', 'no_show']
            if new_status not in allowed:
                return Response({"error": f"Invalid status. Allowed: {allowed}"}, status=400)
            instance.status = new_status
            instance.save()
            return Response(self.get_serializer(instance).data)
        return super().partial_update(request, *args, **kwargs)


class LabBookingViewSet(viewsets.ModelViewSet):
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
        
        # Check if user is a lab owner
        from labs.models import Lab
        try:
            lab = Lab.objects.get(user=user)
            qs = LabBooking.objects.filter(lab=lab)
            if lab_id:
                qs = qs.filter(lab_id=lab_id)
            return qs.select_related('patient').order_by("-created_at")
        except Lab.DoesNotExist:
            # Regular patient
            qs = LabBooking.objects.filter(patient=user)
            if lab_id:
                qs = qs.filter(lab_id=lab_id)
            return qs.select_related('patient').order_by("-created_at")

    def partial_update(self, request, *args, **kwargs):
        booking = self.get_object()
        if 'status' in request.data:
            new_status = request.data['status']
            if new_status == 'completed' and 'booking_code' in request.data:
                if booking.booking_code != request.data['booking_code']:
                    return Response({"error": "Invalid booking code"}, status=400)
            booking.status = new_status
            booking.save()
            return Response(self.get_serializer(booking).data)
        return Response({"error": "Only status updates are allowed"}, status=400)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("🔥 LAB BOOKING PAYLOAD:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("❌ VALIDATION ERRORS:", serializer.errors)  # Debug line
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)