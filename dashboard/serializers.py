# dashboard/serializers.py

from rest_framework import serializers
from specialists.models import Specialist
from ASER.models import Insurance, Certifications, Biography
from doctors.models import DoctorAssignment, WorkSchedule, Doctor
from doctors.serializers import DoctorSerializers, UnregisteredDoctorSerializer  # Import UnregisteredDoctorSerializer
from django.contrib.contenttypes.models import ContentType
from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer
from django.db.models import Count, Q
from specialists.serializers import SpecialistSerializer


class AppointmentStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    confirmed = serializers.IntegerField()
    cancelled = serializers.IntegerField()
    completed = serializers.IntegerField()
    no_show = serializers.IntegerField()
    bookings = AppointmentSerializer(many=True, read_only=True)


class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ["id", "name"]


class InsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insurance
        fields = ["id", "entity", "status"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certifications
        fields = ["id", "name", "entity"]


class BiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Biography
        fields = [
            "bio",
            "bio_details",
            "experiance",
            "operaiton"
        ]


class WorkScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "day",
            "date",
            "start_time",
            "end_time"
        ]


class DoctorAssignmentSerializer(serializers.ModelSerializer):
    schedules = WorkScheduleSerializer(many=True, read_only=True)
    doctor = DoctorSerializers(read_only=True)
    unregistered_doctor = UnregisteredDoctorSerializer(read_only=True)
    appointment_stats = serializers.SerializerMethodField()  # ✅ NEW

    class Meta:
        model = DoctorAssignment
        fields = [
            "id",
            "status",
            "doctor",
            "unregistered_doctor",
            "schedules",
            "appointment_stats",  
            "created_at"
        ]

    def get_appointment_stats(self, obj):
        from appointments.models import Appointment
        from appointments.serializers import AppointmentSerializer
        from django.db.models import Count, Q

        appointment_qs = Appointment.objects.filter(assignment=obj).select_related('patient', 'schedule')
        stats = appointment_qs.aggregate(
            total=Count("id"),
            confirmed=Count("id", filter=Q(status="confirmed")),
            cancelled=Count("id", filter=Q(status="cancelled")),
            completed=Count("id", filter=Q(status="completed")),
            no_show=Count("id", filter=Q(status="no_show")),
        )
        stats['bookings'] = AppointmentSerializer(appointment_qs.order_by('-appointment_date', '-appointment_time'), many=True).data
        return stats


class EntitySerializer(serializers.ModelSerializer):
    specialists = SpecialistSerializer(many=True, read_only=True)
    insurance = InsuranceSerializer(many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)
    about = BiographySerializer(read_only=True)
    appointment_stats = serializers.SerializerMethodField()
    assignments = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = "__all__"

    def get_image_url(self, obj):
        if hasattr(obj, 'image') and obj.image:
            return obj.image.url if hasattr(obj.image, 'url') else str(obj.image)
        return None

    def get_assignments(self, obj):
        # If the entity is a Doctor, use doctor_id directly (personal + entity assignments)
        if isinstance(obj, Doctor):
            assignments = DoctorAssignment.objects.filter(
                doctor=obj
            ).prefetch_related("schedules")
        else:
            content_type = ContentType.objects.get_for_model(obj)
            assignments = DoctorAssignment.objects.filter(
                content_type=content_type,
                object_id=obj.id
            ).prefetch_related("schedules")
        return DoctorAssignmentSerializer(assignments, many=True).data

    def get_appointment_stats(self, obj):
        if isinstance(obj, Doctor):
            assignments = DoctorAssignment.objects.filter(doctor=obj)
        else:
            content_type = ContentType.objects.get_for_model(obj)
            assignments = DoctorAssignment.objects.filter(
                content_type=content_type,
                object_id=obj.id
            )
        appointment_qs = Appointment.objects.filter(
            assignment__in=assignments
        ).select_related('patient', 'assignment', 'schedule')
        stats = appointment_qs.aggregate(
            total=Count("id"),
            confirmed=Count("id", filter=Q(status="confirmed")),
            cancelled=Count("id", filter=Q(status="cancelled")),
            completed=Count("id", filter=Q(status="completed")),
            no_show=Count("id", filter=Q(status="no_show")),
        )
        stats['bookings'] = appointment_qs.order_by('-appointment_date', '-appointment_time')
        return AppointmentStatsSerializer(stats).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if hasattr(instance, 'specialist'):
            specialist = instance.specialist
            if specialist:
                data['specialist'] = {
                    'id': specialist.id,
                    'name': specialist.name
                }
            else:
                data['specialist'] = None
        return data