from rest_framework import serializers
from .models import Appointment,LabBooking
from doctors.models import DoctorAssignment



class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    assignment_display = serializers.StringRelatedField(
    source="assignment",
    read_only=True
    )

    assignment = serializers.PrimaryKeyRelatedField(
        queryset=DoctorAssignment.objects.all()
    )

    appointment_date = serializers.DateField(
        input_formats=["%Y-%m-%d"]
    )

    appointment_time = serializers.TimeField(
        input_formats=["%H:%M", "%H:%M:%S"]
    )

    class Meta:
        model = Appointment
        fields = [
            "id",
            "assignment",
            "assignment_display",
            "schedule",
            "patient",
            "appointment_date",
            "appointment_time",
            "status",
            "booking_code"
        ]
        read_only_fields = ["id", "status"]

    def validate(self, data):
        assignment = data.get("assignment")
        schedule = data.get("schedule")
        appointment_date = data.get("appointment_date")
        appointment_time = data.get("appointment_time")

        # حماية من None
        if not assignment:
            raise serializers.ValidationError({
                "assignment": "Assignment is required"
            })

        # Doctor Verification
        if assignment.doctor:
            if not assignment.doctor.is_verified:
                raise serializers.ValidationError({
                    "detail": "الطبيب غير مفعل حالياً"
                })

        if assignment.unregistered_doctor:
            if not assignment.unregistered_doctor.allow_online_booking:
                raise serializers.ValidationError({
                    "detail": "هذا الطبيب لا يستقبل حجوزات أونلاين"
                })

        # Slot Check
        exists = Appointment.objects.filter(
            schedule=schedule,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=["pending", "confirmed"]
        ).exists()

        if exists:
            raise serializers.ValidationError({
                "detail": "هذا الموعد محجوز مسبقاً"
            })

        return data


class LabBookingSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = LabBooking
        fields = ["id", "patient", "lab", "service_name", "booking_code", "status", "created_at"]
        read_only_fields = ["id", "booking_code", "status", "created_at"]

    def validate(self, data):
        if not data.get("service_name"):
            raise serializers.ValidationError({"service_name": "اسم الخدمة مطلوب للحجز"})
        if not data.get("lab"):
            raise serializers.ValidationError({"lab": "يجب اختيار المختبر"})
        return data