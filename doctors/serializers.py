# doctors/serializers.py

from rest_framework import serializers

from ASER.serializers import CertificationsSerializer, InsuranceSerializer
from .models import Doctor, UnregisteredDoctor, DoctorAssignment, WorkSchedule
from specialists.serializers import SpecialistSerializer

class DoctorSerializers(serializers.ModelSerializer):
    specialist = SpecialistSerializer(read_only=True)
    profile_image = serializers.SerializerMethodField()
    insurance = InsuranceSerializer(many=True, read_only=True)
    certificates = CertificationsSerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_image', 
                  'specialist', 'is_verified', 'insurance', 'certificates']

    def get_profile_image(self, obj):
        # If profile_image is a Cloudinary resource object, get its URL
        if obj.profile_image:
            if hasattr(obj.profile_image, 'url'):
                return obj.profile_image.url
            # If it's already a string (full URL or public ID)
            if isinstance(obj.profile_image, str):
                # If it's a full URL, return it
                if obj.profile_image.startswith('http'):
                    return obj.profile_image
                # Otherwise, assume it's a public ID and build URL
                from django.conf import settings
                cloud_name = getattr(settings, 'CLOUDINARY_CLOUD_NAME', 'drswiflul')
                return f"https://res.cloudinary.com/{cloud_name}/image/upload/{obj.profile_image}"
        return None



class UnregisteredDoctorSerializer(serializers.ModelSerializer):
    specialist = SpecialistSerializer()
    profile_image = serializers.SerializerMethodField()
    
    class Meta:
        model = UnregisteredDoctor
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_image', 'specialist', 'is_verified', 'allow_online_booking', 'insurance', 'certificates']
        read_only_fields = ['allow_online_booking']
    
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