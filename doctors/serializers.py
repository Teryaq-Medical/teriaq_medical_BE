# doctors/serializers.py

from rest_framework import serializers

from ASER.serializers import CertificationsSerializer, InsuranceSerializer
from .models import Doctor, UnregisteredDoctor, DoctorAssignment, WorkSchedule
from specialists.serializers import SpecialistSerializer

# doctors/serializers.py

from rest_framework import serializers
from .models import Doctor, DoctorAssignment
from specialists.serializers import SpecialistSerializer
from ASER.serializers import InsuranceSerializer, CertificationsSerializer,BiographySerializer

class DoctorSerializers(serializers.ModelSerializer):
    specialist = SpecialistSerializer(read_only=True)
    insurance = InsuranceSerializer(many=True, read_only=True)
    certificates = CertificationsSerializer(many=True, read_only=True)
    about = BiographySerializer(read_only=True)
    
    # --- ADDED FIELDS ---
    appointment_stats = serializers.SerializerMethodField()
    # --------------------

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'phone_number', 'address', 'profile_image', 
            'license_document', 'specialist', 'is_verified', 'insurance', 
            'certificates', 'about', 'license_number', 
            'appointment_stats' # <--- MUST BE IN FIELDS
        ]

    def get_appointment_stats(self, obj):
        """
        Calculates stats for all appointments belonging to this doctor.
        """
        from appointments.models import Appointment
        from dashboard.serializers import AppointmentStatsSerializer
        from django.db.models import Count, Q

        # Filter appointments where the assignment belongs to this specific doctor
        appointment_qs = Appointment.objects.filter(
            assignment__doctor=obj
        ).select_related('patient', 'assignment', 'schedule')

        stats = appointment_qs.aggregate(
            total=Count("id"),
            confirmed=Count("id", filter=Q(status="confirmed")),
            cancelled=Count("id", filter=Q(status="cancelled")),
            completed=Count("id", filter=Q(status="completed")),
            no_show=Count("id", filter=Q(status="no_show")),
            pending=Count("id", filter=Q(status="pending")), # Your DB showed 'pending'
        )
        
        # Add the list of bookings to the stats dictionary
        stats['bookings'] = appointment_qs.order_by('-appointment_date', '-appointment_time')
        
        return AppointmentStatsSerializer(stats).data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Keep your existing Cloudinary URL logic
        if instance.profile_image:
            if hasattr(instance.profile_image, 'url'):
                data['profile_image'] = instance.profile_image.url
            elif isinstance(instance.profile_image, str):
                if instance.profile_image.startswith('http'):
                    data['profile_image'] = instance.profile_image
                else:
                    from django.conf import settings
                    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'drswiflul')
                    data['profile_image'] = f"https://res.cloudinary.com/{cloud_name}/image/upload/{instance.profile_image}"
        else:
            data['profile_image'] = None
            
        return data

class UnregisteredDoctorSerializer(serializers.ModelSerializer):
    specialist = SpecialistSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField()
    license_document = serializers.SerializerMethodField()  # ✅ changed
    assignments = serializers.SerializerMethodField()
    class Meta:
        model = UnregisteredDoctor
        fields = [
            'id', 'full_name', 'phone_number', 'address', 'profile_image',
            'license_document', 'specialist', 'is_verified', 'allow_online_booking',
            'insurance', 'certificates', 'license_number','assignments'
        ]
        read_only_fields = ['allow_online_booking']
        
    
    def get_assignments(self, obj):
        assignments = obj.assignments.all().select_related('content_type')
        return [{
            'id': a.id,
            'entity_type': a.content_type.model if a.content_type else 'individual',
            'entity_id': a.object_id,
            'entity_name': a.entity_name,
            'status': a.status,
        } for a in assignments]

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url if hasattr(obj.profile_image, 'url') else str(obj.profile_image)
        return None

    def get_license_document(self, obj):
        if not obj.license_document:
            return None
        if hasattr(obj.license_document, 'url'):
            return obj.license_document.url
        raw = str(obj.license_document)
        # Fix malformed "image/upload/http://..." strings
        if raw.startswith('image/upload/http'):
            parts = raw.split('image/upload/')
            if len(parts) > 1:
                return parts[1]
        if raw.startswith('http'):
            return raw
        return f"https://res.cloudinary.com/drswiflul/image/upload/{raw}"
class WorkScheduleSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(queryset=DoctorAssignment.objects.all(), required=True)
    assignment_id = serializers.PrimaryKeyRelatedField(source='assignment', read_only=True)
    date = serializers.DateField(required=True) 

    class Meta:
        model = WorkSchedule
        fields = ['id', 'day', 'start_time', 'end_time', 'date', 'assignment', 'assignment_id']

class DoctorAssignmentSerializer(serializers.ModelSerializer):
    schedules = WorkScheduleSerializer(many=True, read_only=True)
    entity_type = serializers.SerializerMethodField()
    doctor = DoctorSerializers(read_only=True)
    unregistered_doctor = UnregisteredDoctorSerializer(read_only=True)

    class Meta:
        model = DoctorAssignment
        fields = ['id', 'doctor', 'unregistered_doctor', 'status', 'schedules', 'entity_type']

    def get_entity_type(self, obj):
        if obj.content_type:
            return obj.content_type.model
        return "individual"

class DoctorAssignmentStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used exclusively for updating the status of a DoctorAssignment.
    Only the 'status' field is writable; the 'id' is read-only.
    """
    class Meta:
        model = DoctorAssignment
        fields = ['id', 'status']
        read_only_fields = ['id']