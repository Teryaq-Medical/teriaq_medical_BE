# entities/views.py

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from doctors.models import Doctor, UnregisteredDoctor, DoctorAssignment
from ASER.serializers import InsuranceWriteSerializer, CertificationsWriteSerializer
from ASER.models import Insurance, Certifications, Biography
from cloudinary.uploader import upload
import sys
import traceback

logger = logging.getLogger(__name__)


# ==================== ENTITY UPDATE (Basic Info) ====================
# entities/views.py – replace EntityUpdateView

# entities/views.py

class EntityUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
            "labs": "labs.Lab",
            "doctors": "doctors.Doctor",
            "un-doctors": "doctors.UnregisteredDoctor"
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def upload_base64_image(self, base64_str):
        """
        Upload base64 image to Cloudinary and return the public ID.
        If the input is already a URL, extract public ID or return as is.
        """
        if not base64_str or not isinstance(base64_str, str):
            return None
    
    # If it's already a full URL, try to extract public ID
        if base64_str.startswith('http://') or base64_str.startswith('https://'):
        # Extract public ID from Cloudinary URL
        # Example: https://res.cloudinary.com/cloud_name/image/upload/v123/public_id.jpg
            import re
            match = re.search(r'/image/upload/(?:v\d+/)?([^/.]+)', base64_str)
            if match:
                return match.group(1)
            return base64_str  # fallback
    
    # If it's a base64 data URL
        if base64_str.startswith('data:image'):
            try:
                result = upload(base64_str)
            # Return the public ID (not the full URL)
                return result.get('public_id')
            except Exception as e:
                print(f"❌ Cloudinary upload failed: {e}")
                return None
    
    # If it's already a public ID (no slashes, alphanumeric), return as is
        if re.match(r'^[a-zA-Z0-9_]+$', base64_str):
            return base64_str
    
        return None

    def put(self, request, entity_type, id):
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=400)

        try:
            if request.user.is_staff or request.user.is_superuser:
                entity = model.objects.get(id=id)
            else:
                entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or no permission"}, status=404)

        # Copy request data to avoid mutation
        data = request.data.copy()

        # Handle image uploads for labs/hospitals/clinics
        if 'image' in data:
            try:
                uploaded_url = self.upload_base64_image(data['image'])
                if uploaded_url:
                    data['image'] = uploaded_url
            except Exception as e:
                return Response({"error": f"Image upload failed: {str(e)}"}, status=400)

        # Handle profile_image for doctors/un-doctors
        if 'profile_image' in data:
            try:
                uploaded_url = self.upload_base64_image(data['profile_image'])
                if uploaded_url:
                    data['profile_image'] = uploaded_url
            except Exception as e:
                return Response({"error": f"Profile image upload failed: {str(e)}"}, status=400)

        # Map common field names to doctor/un-doctor specific field names
        if entity_type in ["doctors", "un-doctors"]:
            if 'name' in data:
                data['full_name'] = data.pop('name')
            if 'phone' in data:
                data['phone_number'] = data.pop('phone')
            # 'address' and 'email' are the same, no mapping needed
            # 'description' is not a field on Doctor/UnregisteredDoctor model – remove it
            data.pop('description', None)

    # Use serializer for update
        serializer_class = self.get_serializer_class(entity_type)
        serializer = serializer_class(entity, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def get_serializer_class(self, entity_type):
        from hospitals.serializers import HospitalSerializers
        from clincs.serializers import ClincsSerializer
        from labs.serializers import LabsSerializers
        from doctors.serializers import DoctorSerializers,UnregisteredDoctorSerializer
        mapping = {
            "hospitals": HospitalSerializers,
            "clincs": ClincsSerializer,
            "labs": LabsSerializers,
            "doctors": DoctorSerializers,
            "un-doctors": UnregisteredDoctorSerializer,

        }
        return mapping.get(entity_type)
# ==================== ENTITY ABOUT UPDATE (FIXED) ====================
class EntityAboutUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
            "labs": "labs.Lab",
            "doctors": "doctors.Doctor",
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def put(self, request, entity_type, id):
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        about_data = request.data
        bio_details = about_data.get('bio_details', '')

        if entity.about:
            # Update existing about – only update provided fields
            if 'bio_details' in about_data:
                entity.about.bio_details = bio_details
            if 'bio' in about_data:
                entity.about.bio = about_data['bio']
            if 'experiance' in about_data:
                entity.about.experiance = about_data['experiance']
            if 'operaiton' in about_data:
                entity.about.operaiton = about_data['operaiton']
            entity.about.save()
        else:
            # Create new about with defaults
            about = Biography.objects.create(
                created_by=request.user,
                bio=about_data.get('bio', ''),
                bio_details=bio_details,
                experiance=about_data.get('experiance', 0),
                operaiton=about_data.get('operaiton', 0)
            )
            entity.about = about
            entity.save()

        return Response({"message": "About updated successfully"}, status=status.HTTP_200_OK)


# ==================== ENTITY INSURANCE (Hospitals, Clinics, Labs) ====================
class EntityInsuranceView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
            "labs": "labs.Lab",
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def post(self, request, entity_type, id):
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        serializer = InsuranceWriteSerializer(data=request.data)
        if serializer.is_valid():
            insurance = serializer.save(created_by=request.user)
            entity.insurance.add(insurance)
            from ASER.serializers import InsuranceSerializer
            return Response(InsuranceSerializer(insurance).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, entity_type, id, insurance_id):
        logger.info("=" * 50)
        logger.info("EntityInsuranceView DELETE called")
        logger.info(f"Entity type: {entity_type}, ID: {id}, Insurance ID: {insurance_id}")

        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
            logger.info(f"Entity found: {entity.name if hasattr(entity, 'name') else entity.id}")
        except model.DoesNotExist:
            logger.error("Entity not found or permission denied")
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        try:
            insurance = Insurance.objects.get(id=insurance_id)
            logger.info(f"Insurance found: {insurance.entity} (ID: {insurance.id})")
            entity.insurance.remove(insurance)
            logger.info("Insurance removed from entity")

            # Check if any other entity still uses this insurance
            from doctors.models import Doctor
            from hospitals.models import Hospital
            from clincs.models import Clinic
            from labs.models import Lab

            used_elsewhere = False
            if Doctor.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                logger.info("Insurance still used by a doctor")
            if Hospital.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                logger.info("Insurance still used by a hospital")
            if Clinic.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                logger.info("Insurance still used by a clinic")
            if Lab.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                logger.info("Insurance still used by a lab")

            if not used_elsewhere:
                insurance.delete()
                logger.info(f"Insurance {insurance.id} deleted (no other references)")
                return Response({"message": "Insurance removed and deleted"}, status=status.HTTP_200_OK)
            else:
                logger.info(f"Insurance {insurance.id} kept (used elsewhere)")
                return Response({"message": "Insurance removed from entity but kept (used by other entities)"},
                                status=status.HTTP_200_OK)

        except Insurance.DoesNotExist:
            logger.error(f"Insurance with id {insurance_id} not found")
            return Response({"error": "Insurance not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error removing insurance: {str(e)}")
            return Response({"error": f"Failed to remove insurance: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== ENTITY CERTIFICATE (All entities including doctors) ====================
class EntityCertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
            "labs": "labs.Lab",
            "doctors": "doctors.Doctor",
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def post(self, request, entity_type, id):
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        serializer = CertificationsWriteSerializer(data=request.data)
        if serializer.is_valid():
            certificate = serializer.save(created_by=request.user)
            entity.certificates.add(certificate)
            from ASER.serializers import CertificationsSerializer
            return Response(CertificationsSerializer(certificate).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, entity_type, id, cert_id):
        logger.info("=" * 50)
        logger.info("EntityCertificateView DELETE called")
        logger.info(f"Entity type: {entity_type}, ID: {id}, Certificate ID: {cert_id}")

        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
            logger.info(f"Entity found: {entity.name if hasattr(entity, 'name') else entity.id}")
        except model.DoesNotExist:
            logger.error("Entity not found or permission denied")
            return Response({"error": "Entity not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        try:
            certificate = Certifications.objects.get(id=cert_id)
            logger.info(f"Certificate found: {certificate.name} (ID: {certificate.id})")
            entity.certificates.remove(certificate)
            logger.info("Certificate removed from entity")

            # Check if any other entity still uses this certificate
            from doctors.models import Doctor
            from hospitals.models import Hospital
            from clincs.models import Clinic
            from labs.models import Lab

            used_elsewhere = False
            if Doctor.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                logger.info("Certificate still used by a doctor")
            if Hospital.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                logger.info("Certificate still used by a hospital")
            if Clinic.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                logger.info("Certificate still used by a clinic")
            if Lab.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                logger.info("Certificate still used by a lab")

            if not used_elsewhere:
                certificate.delete()
                logger.info(f"Certificate {certificate.id} deleted (no other references)")
                return Response({"message": "Certificate removed and deleted"}, status=status.HTTP_200_OK)
            else:
                logger.info(f"Certificate {certificate.id} kept (used elsewhere)")
                return Response({"message": "Certificate removed from entity but kept (used by other entities)"},
                                status=status.HTTP_200_OK)

        except Certifications.DoesNotExist:
            logger.error(f"Certificate with id {cert_id} not found")
            return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Error removing certificate: {str(e)}")
            return Response({"error": f"Failed to remove certificate: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== ENTITY SPECIALIST (Hospitals/Clinics only) ====================
class EntitySpecialistView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def post(self, request, entity_type, id):
        from specialists.models import Specialist
        from specialists.serializers import SpecialistSerializer

        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        specialist_name = request.data.get('name')
        if not specialist_name:
            return Response({"error": "Specialist name is required"}, status=status.HTTP_400_BAD_REQUEST)

        specialist, created = Specialist.objects.get_or_create(name=specialist_name)
        entity.specialists.add(specialist)
        return Response(SpecialistSerializer(specialist).data, status=status.HTTP_201_CREATED)

    def delete(self, request, entity_type, id, specialist_id):
        from specialists.models import Specialist

        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        try:
            specialist = Specialist.objects.get(id=specialist_id)
            entity.specialists.remove(specialist)
            return Response({"message": "Specialist removed successfully"}, status=status.HTTP_200_OK)
        except Specialist.DoesNotExist:
            return Response({"error": "Specialist not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== DOCTOR ASSIGNMENT (Hospitals/Clinics only) ====================
class EntityDoctorAssignmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get_model(self, entity_type):
        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
        }
        model_path = mapping.get(entity_type.lower())
        if not model_path:
            return None
        app_label, model_name = model_path.split(".")
        return apps.get_model(app_label, model_name)

    def post(self, request, entity_type, id):
        from specialists.models import Specialist
        from cloudinary.uploader import upload
        from doctors.models import WorkSchedule
        from datetime import date

        print(f"📥 Received data: {request.data}")
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        doctor_type = request.data.get('doctor_type')
        schedules_data = request.data.get('schedules', [])
        print(f"📌 Doctor type: {doctor_type}, Schedules: {schedules_data}")

        assignment = None

        if doctor_type == 'registered':
            doctor_id = request.data.get('doctor_id')
            if not doctor_id:
                return Response({"error": "Doctor ID is required for registered doctor"},
                              status=status.HTTP_400_BAD_REQUEST)
            try:
                doctor = Doctor.objects.get(id=doctor_id)
            except Doctor.DoesNotExist:
                return Response({"error": f"Doctor with ID {doctor_id} not found"},
                              status=status.HTTP_404_NOT_FOUND)

            content_type = ContentType.objects.get_for_model(entity)
            assignment, created = DoctorAssignment.objects.get_or_create(
                doctor=doctor,
                content_type=content_type,
                object_id=entity.id,
                defaults={'status': 'approved'}
            )

        elif doctor_type == 'unregistered':
            required_fields = ['full_name', 'specialist_name', 'phone_number', 'address', 'license_number']
            missing_fields = [field for field in required_fields if field not in request.data]
            if missing_fields:
                return Response({"error": f"Missing required fields: {missing_fields}",
                                 "received_fields": list(request.data.keys())},
                                status=status.HTTP_400_BAD_REQUEST)

            specialist_name = request.data.get('specialist_name')
            specialist, created = Specialist.objects.get_or_create(name=specialist_name)

            profile_image = ''
            if 'profile_image' in request.data and request.data['profile_image']:
                try:
                    profile_image = self.handle_image_upload(request.data['profile_image'])
                except Exception as e:
                    print(f"Error uploading profile image: {e}")

            license_document = ''
            if 'license_document' in request.data and request.data['license_document']:
                try:
                    license_document = self.handle_image_upload(request.data['license_document'])
                except Exception as e:
                    print(f"Error uploading license document: {e}")

            try:
                unregistered_doctor = UnregisteredDoctor.objects.create(
                    full_name=request.data['full_name'],
                    specialist=specialist,
                    phone_number=request.data['phone_number'],
                    address=request.data['address'],
                    license_number=request.data['license_number'],
                    profile_image=profile_image,
                    license_document=license_document,
                    allow_online_booking=False,
                    is_verified=False
                )
                print(f"✅ Created unregistered doctor with ID: {unregistered_doctor.id}")
            except Exception as e:
                print(f"❌ Error creating unregistered doctor: {str(e)}")
                return Response({"error": f"Failed to create doctor: {str(e)}"},
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            content_type = ContentType.objects.get_for_model(entity)
            assignment = DoctorAssignment.objects.create(
                unregistered_doctor=unregistered_doctor,
                content_type=content_type,
                object_id=entity.id,
                status='pending'
            )

        else:
            return Response({"error": "doctor_type must be 'registered' or 'unregistered'",
                             "received_doctor_type": doctor_type},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create schedules for the assignment
        for schedule_data in schedules_data:
            day = schedule_data.get('day')
            start_time = schedule_data.get('start_time')
            end_time = schedule_data.get('end_time')
            if day and start_time and end_time:
                schedule_date = date.today()
                try:
                    WorkSchedule.objects.create(
                        assignment=assignment,
                        day=day,
                        start_time=start_time,
                        end_time=end_time,
                        date=schedule_date
                    )
                    print(f"✅ Schedule created for assignment {assignment.id}")
                except Exception as e:
                    print(f"❌ Error creating schedule: {str(e)}")
                    import traceback
                    traceback.print_exc()

        from doctors.serializers import DoctorAssignmentSerializer
        try:
            serializer = DoctorAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"❌ Serialization error: {str(e)}")
            traceback.print_exc()
            return Response({"error": f"Serialization failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_image_upload(self, image_data):
        from cloudinary.uploader import upload
        if isinstance(image_data, str):
            if image_data.startswith('http://') or image_data.startswith('https://'):
                return image_data
            try:
                if image_data.startswith('data:image'):
                    upload_result = upload(image_data)
                    return upload_result['url']
                elif len(image_data) > 100:
                    upload_result = upload(f"data:image/jpeg;base64,{image_data}")
                    return upload_result['url']
            except Exception as e:
                print(f"Upload error: {e}")
                raise e
        return ''

    def delete(self, request, entity_type, id, assignment_id):
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        try:
            assignment = DoctorAssignment.objects.get(id=assignment_id, object_id=entity.id)
            if assignment.unregistered_doctor:
                unregistered_doctor = assignment.unregistered_doctor
                assignment.delete()
                unregistered_doctor.delete()
            else:
                assignment.delete()
            return Response({"message": "Doctor removed successfully"}, status=status.HTTP_200_OK)
        except DoctorAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)


# ==================== DOCTOR SPECIALIST (Single FK) ====================
class DoctorSpecialistView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, doctor_id):
        from specialists.models import Specialist

        try:
            doctor = Doctor.objects.get(id=doctor_id, user=request.user)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        specialist_name = request.data.get('name')
        if not specialist_name:
            return Response({"error": "Specialist name is required"},
                          status=status.HTTP_400_BAD_REQUEST)

        specialist, created = Specialist.objects.get_or_create(name=specialist_name)
        doctor.specialist = specialist
        doctor.save()
        from specialists.serializers import SpecialistSerializer
        return Response(SpecialistSerializer(specialist).data, status=status.HTTP_200_OK)


# ==================== DOCTOR SCHEDULE ====================
class DoctorScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def get_doctor(self, doctor_id, user):
        try:
            return Doctor.objects.get(id=doctor_id, user=user)
        except Doctor.DoesNotExist:
            return None

    def post(self, request, doctor_id):
        from doctors.models import WorkSchedule
        from datetime import date, datetime, timedelta

        print(f"📥 DoctorScheduleView POST called with doctor_id: {doctor_id}")
        doctor = self.get_doctor(doctor_id, request.user)
        if not doctor:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        content_type = ContentType.objects.get_for_model(doctor)
        assignment, created = DoctorAssignment.objects.get_or_create(
            doctor=doctor,
            content_type=content_type,
            object_id=doctor.id,
            defaults={'status': 'approved'}
        )

        required_fields = ['day', 'start_time', 'end_time']
        missing_fields = [field for field in required_fields if field not in request.data]
        if missing_fields:
            return Response({"error": f"Missing required fields: {missing_fields}"},
                          status=status.HTTP_400_BAD_REQUEST)

        day_mapping = {
            'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
            'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
            'mon': 'mon', 'tue': 'tue', 'wed': 'wed', 'thu': 'thu',
            'fri': 'fri', 'sat': 'sat', 'sun': 'sun'
        }
        day = request.data.get('day').lower()
        day_code = day_mapping.get(day, day)
        valid_days = ['sat', 'sun', 'mon', 'tue', 'wed', 'thu', 'fri']
        if day_code not in valid_days:
            return Response({"error": f"Invalid day. Must be one of: {valid_days}"},
                          status=status.HTTP_400_BAD_REQUEST)

        schedule_date = request.data.get('date')
        if not schedule_date:
            today = date.today()
            days_ahead = (valid_days.index(day_code) - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            schedule_date = today + timedelta(days=days_ahead)
        else:
            try:
                schedule_date = datetime.strptime(schedule_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD"},
                              status=status.HTTP_400_BAD_REQUEST)

        try:
            schedule = WorkSchedule.objects.create(
                assignment=assignment,
                day=day_code,
                start_time=request.data.get('start_time'),
                end_time=request.data.get('end_time'),
                date=schedule_date
            )
            from doctors.serializers import WorkScheduleSerializer
            return Response(WorkScheduleSerializer(schedule).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"❌ Error creating schedule: {str(e)}")
            return Response({"error": f"Failed to create schedule: {str(e)}"},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, doctor_id, schedule_id):
        from doctors.models import WorkSchedule

        doctor = self.get_doctor(doctor_id, request.user)
        if not doctor:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        try:
            schedule = WorkSchedule.objects.get(id=schedule_id, assignment__doctor=doctor)
            schedule.delete()
            return Response({"message": "Schedule removed successfully"}, status=status.HTTP_200_OK)
        except WorkSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, doctor_id, schedule_id):
        from doctors.models import WorkSchedule
        from datetime import datetime

        doctor = self.get_doctor(doctor_id, request.user)
        if not doctor:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        try:
            schedule = WorkSchedule.objects.get(id=schedule_id, assignment__doctor=doctor)
            if 'day' in request.data:
                day = request.data['day'].lower()
                day_mapping = {
                    'monday': 'mon', 'tuesday': 'tue', 'wednesday': 'wed',
                    'thursday': 'thu', 'friday': 'fri', 'saturday': 'sat', 'sunday': 'sun',
                    'mon': 'mon', 'tue': 'tue', 'wed': 'wed', 'thu': 'thu',
                    'fri': 'fri', 'sat': 'sat', 'sun': 'sun'
                }
                schedule.day = day_mapping.get(day, day)
            if 'start_time' in request.data:
                schedule.start_time = request.data['start_time']
            if 'end_time' in request.data:
                schedule.end_time = request.data['end_time']
            if 'date' in request.data:
                schedule.date = datetime.strptime(request.data['date'], '%Y-%m-%d').date()
            schedule.save()
            from doctors.serializers import WorkScheduleSerializer
            return Response(WorkScheduleSerializer(schedule).data, status=status.HTTP_200_OK)
        except WorkSchedule.DoesNotExist:
            return Response({"error": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Failed to update schedule: {str(e)}"},
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== DOCTOR CERTIFICATE ====================
class DoctorCertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(id=doctor_id, user=request.user)
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        serializer = CertificationsWriteSerializer(data=request.data)
        if serializer.is_valid():
            certificate = serializer.save(created_by=request.user)
            doctor.certificates.add(certificate)
            from ASER.serializers import CertificationsSerializer
            return Response(CertificationsSerializer(certificate).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, doctor_id, cert_id):
        print("=" * 60, flush=True)
        print("DoctorCertificateView.delete - START", flush=True)
        print(f"doctor_id: {doctor_id} (type: {type(doctor_id)})", flush=True)
        print(f"cert_id: {cert_id} (type: {type(cert_id)})", flush=True)
        print(f"User: {request.user} (ID: {request.user.id})", flush=True)

        try:
            doctor = Doctor.objects.get(id=doctor_id, user=request.user)
            print(f"Doctor found: {doctor.full_name} (ID: {doctor.id})", flush=True)
        except Exception as e:
            print(f"ERROR in Doctor.objects.get: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": "Doctor lookup failed"}, status=500)

        try:
            certificate = Certifications.objects.get(id=cert_id)
            print(f"Certificate found: {certificate.name} (ID: {certificate.id})", flush=True)
        except Exception as e:
            print(f"ERROR in Certifications.objects.get: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": "Certificate lookup failed"}, status=500)

        try:
            print(f"Removing certificate {certificate.id} from doctor {doctor.id}", flush=True)
            doctor.certificates.remove(certificate)
            print("Removal successful", flush=True)
        except Exception as e:
            print(f"ERROR during doctor.certificates.remove(): {e}", flush=True)
            traceback.print_exc()
            return Response({"error": f"Failed to remove certificate: {str(e)}"}, status=500)

        try:
            from doctors.models import Doctor as DocModel
            from hospitals.models import Hospital
            from clincs.models import Clinic
            from labs.models import Lab

            used_elsewhere = False
            if DocModel.objects.filter(certificates=certificate).exclude(id=doctor.id).exists():
                used_elsewhere = True
                print("Certificate still used by another doctor", flush=True)
            if Hospital.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                print("Certificate still used by a hospital", flush=True)
            if Clinic.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                print("Certificate still used by a clinic", flush=True)
            if Lab.objects.filter(certificates=certificate).exists():
                used_elsewhere = True
                print("Certificate still used by a lab", flush=True)

            if not used_elsewhere:
                certificate.delete()
                print(f"Certificate {certificate.id} deleted (no other references)", flush=True)
                return Response({"message": "Certificate removed and deleted"}, status=200)
            else:
                print(f"Certificate {certificate.id} kept (used elsewhere)", flush=True)
                return Response({"message": "Certificate removed from doctor but kept (used by other entities)"}, status=200)

        except Exception as e:
            print(f"ERROR in usage check / deletion: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": f"Failed to complete deletion: {str(e)}"}, status=500)


# ==================== DOCTOR INSURANCE ====================
class DoctorInsuranceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, doctor_id):
        logger.info("=" * 50)
        logger.info("DoctorInsuranceView POST called")
        logger.info(f"Doctor ID: {doctor_id}")
        logger.info(f"Request data: {request.data}")

        try:
            doctor = Doctor.objects.get(id=doctor_id, user=request.user)
            logger.info(f"Doctor found: {doctor.full_name}")
        except Doctor.DoesNotExist:
            return Response({"error": "Doctor not found or you don't have permission"},
                          status=status.HTTP_404_NOT_FOUND)

        if not hasattr(doctor, 'insurance'):
            return Response({"error": "Doctor model doesn't support insurance"},
                          status=status.HTTP_400_BAD_REQUEST)

        serializer = InsuranceWriteSerializer(data=request.data)
        if serializer.is_valid():
            try:
                insurance = serializer.save(created_by=request.user)
                doctor.insurance.add(insurance)
                doctor.save()
                from ASER.serializers import InsuranceSerializer
                return Response(InsuranceSerializer(insurance).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"Failed to add insurance: {str(e)}"},
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, doctor_id, insurance_id):
        print("=" * 60, flush=True)
        print("DoctorInsuranceView.delete - START", flush=True)
        print(f"doctor_id: {doctor_id} (type: {type(doctor_id)})", flush=True)
        print(f"insurance_id: {insurance_id} (type: {type(insurance_id)})", flush=True)
        print(f"User: {request.user} (ID: {request.user.id})", flush=True)

        try:
            doctor = Doctor.objects.get(id=doctor_id, user=request.user)
            print(f"Doctor found: {doctor.full_name} (ID: {doctor.id})", flush=True)
        except Exception as e:
            print(f"ERROR in Doctor.objects.get: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": "Doctor lookup failed"}, status=500)

        try:
            insurance = Insurance.objects.get(id=insurance_id)
            print(f"Insurance found: {insurance.entity} (ID: {insurance.id})", flush=True)
        except Exception as e:
            print(f"ERROR in Insurance.objects.get: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": "Insurance lookup failed"}, status=500)

        try:
            print(f"Removing insurance {insurance.id} from doctor {doctor.id}", flush=True)
            doctor.insurance.remove(insurance)
            print("Removal successful", flush=True)
        except Exception as e:
            print(f"ERROR during doctor.insurance.remove(): {e}", flush=True)
            traceback.print_exc()
            return Response({"error": f"Failed to remove insurance: {str(e)}"}, status=500)

        try:
            from doctors.models import Doctor as DocModel
            from hospitals.models import Hospital
            from clincs.models import Clinic
            from labs.models import Lab

            used_elsewhere = False
            if DocModel.objects.filter(insurance=insurance).exclude(id=doctor.id).exists():
                used_elsewhere = True
                print("Insurance still used by another doctor", flush=True)
            if Hospital.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                print("Insurance still used by a hospital", flush=True)
            if Clinic.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                print("Insurance still used by a clinic", flush=True)
            if Lab.objects.filter(insurance=insurance).exists():
                used_elsewhere = True
                print("Insurance still used by a lab", flush=True)

            if not used_elsewhere:
                insurance.delete()
                print(f"Insurance {insurance.id} deleted (no other references)", flush=True)
                return Response({"message": "Insurance removed and deleted"}, status=200)
            else:
                print(f"Insurance {insurance.id} kept (used elsewhere)", flush=True)
                return Response({"message": "Insurance removed from doctor but kept (used by other entities)"}, status=200)

        except Exception as e:
            print(f"ERROR in usage check / deletion: {e}", flush=True)
            traceback.print_exc()
            return Response({"error": f"Failed to complete deletion: {str(e)}"}, status=500)