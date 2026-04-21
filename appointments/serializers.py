from rest_framework import serializers
from .models import Appointment, LabBooking
from doctors.models import DoctorAssignment


class AppointmentSerializer(serializers.ModelSerializer):
    patient = serializers.HiddenField(default=serializers.CurrentUserDefault())
    patient_name = serializers.SerializerMethodField()
    assignment_display = serializers.StringRelatedField(source="assignment", read_only=True)
    assignment = serializers.PrimaryKeyRelatedField(queryset=DoctorAssignment.objects.all())
    appointment_date = serializers.DateField(input_formats=["%Y-%m-%d"])
    appointment_time = serializers.TimeField(input_formats=["%H:%M", "%H:%M:%S"])

    class Meta:
        model = Appointment
        fields = [
            "id", "assignment", "assignment_display", "schedule", "patient", "patient_name",
            "appointment_date", "appointment_time", "status", "booking_code"
        ]
        read_only_fields = ["id", "status", "patient_name"]

    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else "Unknown"

    def validate(self, data):
        # ... (keep your existing validate logic)
        return data

class LabBookingSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = LabBooking
        fields = ["id", "patient", "patient_name", "lab", "service_name", "booking_code", "status", "created_at"]
        read_only_fields = ["id", "booking_code", "status", "created_at", "patient_name"]
        extra_kwargs = {
            'patient': {'required': False, 'allow_null': True}
        }

    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else "Unknown"