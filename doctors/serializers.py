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
    about = BiographySerializer()

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'phone_number', 'address', 'profile_image','license_document',
            'specialist', 'is_verified', 'insurance', 'certificates','about','license_number'
        ]

    def to_representation(self, instance):
        """
        Convert the stored public ID (or Cloudinary resource) into a full image URL.
        This ensures the frontend receives a usable URL while the model stores only the public ID.
        """
        data = super().to_representation(instance)
        if instance.profile_image:
            # If it's a Cloudinary resource object, get its URL
            if hasattr(instance.profile_image, 'url'):
                data['profile_image'] = instance.profile_image.url
            # If it's a string (public ID or full URL)
            elif isinstance(instance.profile_image, str):
                if instance.profile_image.startswith('http'):
                    data['profile_image'] = instance.profile_image
                else:
                    # Build the full Cloudinary URL from the public ID
                    from django.conf import settings
                    cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'drswiflul')
                    data['profile_image'] = f"https://res.cloudinary.com/{cloud_name}/image/upload/{instance.profile_image}"
        else:
            data['profile_image'] = None
        return data

    # Remove get_assignments method

class UnregisteredDoctorSerializer(serializers.ModelSerializer):
    specialist = SpecialistSerializer()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = UnregisteredDoctor
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_image','license_document', 'specialist', 'is_verified', 'allow_online_booking', 'insurance', 'certificates','license_number','allow_online_booking','is_verified']
        read_only_fields = []
    
    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url if hasattr(obj.profile_image, 'url') else obj.profile_image
        return None


class WorkScheduleSerializer(serializers.ModelSerializer):
    assignment_id = serializers.PrimaryKeyRelatedField(
        source='assignment', 
        read_only=True
    )
    class Meta:
        model = WorkSchedule
        fields = ['id', 'day', 'start_time', 'end_time', 'assignment_id']
    

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