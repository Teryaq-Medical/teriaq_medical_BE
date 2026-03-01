import logging
from django.db import transaction, IntegrityError
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment,LabBooking
from .serializers import AppointmentSerializer, LabBookingSerializer

logger = logging.getLogger(__name__)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    # permission_classes = [IsAuthenticated]  # enable later

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user
        ).order_by("-created_at")

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        logger.info("========== APPOINTMENT CREATE START ==========")

        logger.info(f"Request method: {request.method}")
        logger.info(f"User: {request.user}")
        logger.info(f"Is authenticated: {request.user.is_authenticated}")
        logger.info(f"Payload: {request.data}")

        serializer = self.get_serializer(data=request.data)

        # 🔎 Step 1 — Field validation
        if not serializer.is_valid():
            logger.error("❌ SERIALIZER FIELD VALIDATION FAILED")
            logger.error(f"Errors: {serializer.errors}")
            logger.info("========== END ==========")
            return Response(serializer.errors, status=400)

        logger.info("✅ Serializer field validation passed")

        # 🔎 Step 2 — Try saving
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