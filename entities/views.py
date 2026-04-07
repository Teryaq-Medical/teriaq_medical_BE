# entities/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from doctors.models import Doctor, UnregisteredDoctor, DoctorAssignment
from ASER.serializers import InsuranceWriteSerializer, CertificationsWriteSerializer, BiographyWriteSerializer
from ASER.models import Insurance, Certifications, Biography
from cloudinary.uploader import upload
import base64
import uuid


class EntityUpdateView(APIView):
    """
    View for updating entity basic information
    PUT /api/entities/<entity_type>/<id>/update/
    """
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

        # Update basic fields
        updatable_fields = ['name', 'address', 'phone', 'email', 'description']
        for field in updatable_fields:
            if field in request.data:
                setattr(entity, field, request.data[field])

        entity.save()
        
        serializer = self.get_serializer(entity, entity_type)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer(self, entity, entity_type):
        from hospitals.serializers import HospitalSerializers
        from clincs.serializers import ClincsSerializer
        from labs.serializers import LabsSerializers
        from doctors.serializers import DoctorSerializers
        
        mapping = {
            "hospitals": HospitalSerializers,
            "clincs": ClincsSerializer,
            "labs": LabsSerializers,
            "doctors": DoctorSerializers,
        }
        serializer_class = mapping.get(entity_type)
        return serializer_class(entity)


class EntityAboutUpdateView(APIView):
    """
    View for updating entity about/bio
    PUT /api/entities/<entity_type>/<id>/about/update/
    """
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
        if entity.about:
            for key, value in about_data.items():
                setattr(entity.about, key, value)
            entity.about.save()
        else:
            about_data['created_by'] = request.user.id
            about_serializer = BiographyWriteSerializer(data=about_data)
            if about_serializer.is_valid():
                entity.about = about_serializer.save()
            else:
                return Response(about_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        entity.save()
        return Response({"message": "About updated successfully"}, status=status.HTTP_200_OK)


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
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        try:
            insurance = Insurance.objects.get(id=insurance_id, created_by=request.user)
            entity.insurance.remove(insurance)
            if insurance.insurance_set.count() == 0:
                insurance.delete()
            return Response({"message": "Insurance removed successfully"}, status=status.HTTP_200_OK)
        except Insurance.DoesNotExist:
            return Response({"error": "Insurance not found"}, status=status.HTTP_404_NOT_FOUND)


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
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        try:
            certificate = Certifications.objects.get(id=cert_id, created_by=request.user)
            entity.certificates.remove(certificate)
            if certificate.certifications_set.count() == 0:
                certificate.delete()
            return Response({"message": "Certificate removed successfully"}, status=status.HTTP_200_OK)
        except Certifications.DoesNotExist:
            return Response({"error": "Certificate not found"}, status=status.HTTP_404_NOT_FOUND)


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




# entities/views.py - Update the EntityDoctorAssignmentView

# entities/views.py - Complete working version

class EntityDoctorAssignmentView(APIView):
    """
    View for managing doctors assigned to entity
    Supports both registered doctors (by ID) and unregistered doctors (with full data)
    """
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
        
        print(f"📥 Received data: {request.data}")  # Debug log
        
        model = self.get_model(entity_type)
        if not model:
            return Response({"error": "Invalid entity type"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            entity = model.objects.get(id=id, user=request.user)
        except model.DoesNotExist:
            return Response({"error": "Entity not found or you don't have permission"}, 
                          status=status.HTTP_404_NOT_FOUND)

        doctor_type = request.data.get('doctor_type')
        print(f"📌 Doctor type: {doctor_type}")
        
        # Handle registered doctor
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
            
            from doctors.serializers import DoctorAssignmentSerializer
            serializer = DoctorAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # Handle unregistered doctor
        elif doctor_type == 'unregistered':
            # Define required fields - allow_online_booking is NOT required
            required_fields = ['full_name', 'specialist_name', 'phone_number', 'address', 'license_number']
            
            # Check which required fields are missing
            missing_fields = [field for field in required_fields if field not in request.data]
            
            if missing_fields:
                return Response({
                    "error": f"Missing required fields: {missing_fields}",
                    "received_fields": list(request.data.keys())
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get or create specialist
            specialist_name = request.data.get('specialist_name')
            specialist, created = Specialist.objects.get_or_create(name=specialist_name)
            
            # Handle profile image (optional)
            profile_image = ''
            if 'profile_image' in request.data and request.data['profile_image']:
                try:
                    profile_image = self.handle_image_upload(request.data['profile_image'])
                except Exception as e:
                    print(f"Error uploading profile image: {e}")
            
            # Handle license document (optional)
            license_document = ''
            if 'license_document' in request.data and request.data['license_document']:
                try:
                    license_document = self.handle_image_upload(request.data['license_document'])
                except Exception as e:
                    print(f"Error uploading license document: {e}")
            
            # Create unregistered doctor
            try:
                unregistered_doctor = UnregisteredDoctor.objects.create(
                    full_name=request.data['full_name'],
                    specialist=specialist,
                    phone_number=request.data['phone_number'],
                    address=request.data['address'],
                    license_number=request.data['license_number'],
                    profile_image=profile_image,
                    license_document=license_document,
                    allow_online_booking=False,  # Always False for owner-added doctors
                    is_verified=False
                )
                print(f"✅ Created unregistered doctor with ID: {unregistered_doctor.id}")
            except Exception as e:
                print(f"❌ Error creating unregistered doctor: {str(e)}")
                return Response({"error": f"Failed to create doctor: {str(e)}"}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Create assignment
            content_type = ContentType.objects.get_for_model(entity)
            assignment = DoctorAssignment.objects.create(
                unregistered_doctor=unregistered_doctor,
                content_type=content_type,
                object_id=entity.id,
                status='pending'
            )
            
            from doctors.serializers import DoctorAssignmentSerializer
            serializer = DoctorAssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        else:
            return Response({
                "error": "doctor_type must be 'registered' or 'unregistered'",
                "received_doctor_type": doctor_type
            }, status=status.HTTP_400_BAD_REQUEST)

    def handle_image_upload(self, image_data):
        """Handle base64 image upload to Cloudinary"""
        from cloudinary.uploader import upload
        
        # If it's already a URL, return as is
        if isinstance(image_data, str):
            if image_data.startswith('http://') or image_data.startswith('https://'):
                return image_data
            
            # Handle base64 upload
            try:
                # If it's a data URL
                if image_data.startswith('data:image'):
                    upload_result = upload(image_data)
                    return upload_result['url']
                # If it's raw base64
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
            # If it's an unregistered doctor, delete the doctor record too
            if assignment.unregistered_doctor:
                unregistered_doctor = assignment.unregistered_doctor
                assignment.delete()
                unregistered_doctor.delete()
            else:
                assignment.delete()
            return Response({"message": "Doctor removed successfully"}, status=status.HTTP_200_OK)
        except DoctorAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=status.HTTP_404_NOT_FOUND)