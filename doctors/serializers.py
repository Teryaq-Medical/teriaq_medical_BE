# doctors/serializers.py - Ensure no validation requires allow_online_booking

from rest_framework import serializers
from .models import Doctor, UnregisteredDoctor, DoctorAssignment, WorkSchedule
from specialists.serializers import SpecialistSerializer

class DoctorSerializers(serializers.ModelSerializer):
    specialist = SpecialistSerializer()
    class Meta:
        model = Doctor
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_image', 'specialist', 'is_verified']


class UnregisteredDoctorSerializer(serializers.ModelSerializer):
    specialist = SpecialistSerializer()
    class Meta:
        model = UnregisteredDoctor
        fields = ['id', 'full_name', 'phone_number', 'address', 'profile_image', 'specialist', 'is_verified', 'allow_online_booking']
        read_only_fields = ['allow_online_booking']  # Make it read-only for non-admin users


class WorkScheduleSerializer(serializers.ModelSerializer):
    assignment_id = serializers.PrimaryKeyRelatedField(
        source='assignment', 
        read_only=True
    )
    class Meta:
        model = WorkSchedule
        fields = ['id', 'day', 'start_time', 'end_time', 'assignment_id']
    

class DoctorAssignmentSerializer(serializers.ModelSerializer):
    doctor_info = serializers.SerializerMethodField()
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

    def get_doctor_info(self, obj):
        doctor = obj.doctor if obj.doctor else obj.unregistered_doctor
        if not doctor:
            return None

        image_url = None
        if obj.doctor and obj.doctor.profile_image:
            if hasattr(obj.doctor.profile_image, 'url'):
                image_url = obj.doctor.profile_image.url
            else:
                image_url = obj.doctor.profile_image
        elif obj.unregistered_doctor and hasattr(obj.unregistered_doctor, 'profile_image'):
            if obj.unregistered_doctor.profile_image:
                if hasattr(obj.unregistered_doctor.profile_image, 'url'):
                    image_url = obj.unregistered_doctor.profile_image.url
                else:
                    image_url = obj.unregistered_doctor.profile_image

        name = "Unknown"
        if hasattr(doctor, 'full_name'):
            name = doctor.full_name
        elif hasattr(doctor, 'user') and hasattr(doctor.user, 'full_name'):
            name = doctor.user.full_name

        return {
            "assignment_id": obj.id,
            "doctor_id": doctor.id if hasattr(doctor, 'id') else None,
            "name": name,
            "specialty": [doctor.specialist.name] if hasattr(doctor, 'specialist') and doctor.specialist else [],
            "image": image_url,
            "is_registered": obj.doctor is not None,
        }