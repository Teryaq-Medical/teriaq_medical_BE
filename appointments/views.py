# appointments/views.py

import logging
from django.db import transaction, IntegrityError
from rest_framework import viewsets, status
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
        
        # If user is staff/admin, see all appointments
        if user.is_staff:
            return Appointment.objects.all().order_by("-created_at")
        
        # If user is a patient (normal user), see their own appointments
        if user.user_type == "normal":
            return Appointment.objects.filter(
                patient=user
            ).order_by("-created_at")
        
        # If user is an entity owner (hospital, clinic, doctor, lab)
        # Get appointments for their entity
        if user.user_type in ["hospitals", "clincs", "doctors", "labs"]:
            from django.contrib.contenttypes.models import ContentType
            from doctors.models import DoctorAssignment
            
            # Get the entity model based on user_type
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
            
            content_type = ContentType.objects.get_for_model(entity)
            
            # Get all assignments for this entity
            assignments = DoctorAssignment.objects.filter(
                content_type=content_type,
                object_id=entity.id
            )
            
            # Return appointments for these assignments
            return Appointment.objects.filter(
                assignment__in=assignments
            ).order_by("-created_at")
        
        return Appointment.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        logger.info("========== APPOINTMENT CREATE START ==========")
        logger.info(f"Request method: {request.method}")
        logger.info(f"User: {request.user}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info(f"Payload: {request.data}")

        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            logger.error("❌ SERIALIZER FIELD VALIDATION FAILED")
            logger.error(f"Errors: {serializer.errors}")
            logger.info("========== END ==========")
            return Response(serializer.errors, status=400)

        logger.info("✅ Serializer field validation passed")

        try:
            logger.info("💾 Attempting to save appointment...")
            self.perform_create(serializer)
            logger.info("✅ Appointment saved successfully")

        except IntegrityError as e:
            logger.error("🔥 DATABASE INTEGRITY ERROR")
            logger.error(str(e))
            logger.info("========== END ==========")
            return Response(
                {"detail": "Database integrity error"},
                status=400
            )

        except Exception as e:
            logger.exception("💥 UNEXPECTED ERROR")
            logger.info("========== END ==========")
            return Response(
                {"detail": "Unexpected server error"},
                status=500
            )

        logger.info("========== APPOINTMENT CREATE SUCCESS ==========")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        logger.info("🔧 Inside perform_create")
        logger.info(f"Saving with user: {self.request.user}")
        serializer.save(patient=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        """Override partial_update to validate booking code for completion"""
        instance = self.get_object()
        
        # Get the requested new status
        new_status = request.data.get('status')
        booking_code = request.data.get('booking_code')
        
        # If completing the appointment, validate booking code
        if new_status == 'completed':
            # Check if booking code is provided
            if not booking_code:
                return Response(
                    {"error": "Booking code is required to complete appointment"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate booking code matches
            if instance.booking_code != booking_code:
                return Response(
                    {"error": "Invalid booking code. Please check and try again."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update status to completed
            instance.status = 'completed'
            instance.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        # For other status updates (confirm, cancel, etc.)
        elif new_status:
            # Validate allowed status transitions
            allowed_statuses = ['confirmed', 'cancelled', 'no_show']
            if new_status not in allowed_statuses:
                return Response(
                    {"error": f"Invalid status. Allowed: {allowed_statuses}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            instance.status = new_status
            instance.save()
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        # If no status, proceed with normal update
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Override update to use the same validation logic"""
        return self.partial_update(request, *args, **kwargs)
        


class LabBookingViewSet(viewsets.ModelViewSet):
    serializer_class = LabBookingSerializer

    def get_queryset(self):
        return LabBooking.objects.filter(patient=self.request.user).order_by("-created_at")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("🔥 LAB BOOKING PAYLOAD:", request.data)

        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            print("❌ LAB BOOKING VALIDATION FAILED:", e.detail)
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(patient=self.request.user)
        print("✅ LAB BOOKING CREATED:", serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)