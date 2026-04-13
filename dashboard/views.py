# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from doctors.models import Doctor
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from appointments.models import Appointment, LabBooking
from django.apps import apps
from .serializers import EntitySerializer
from ASER.viewset import TeriaqViewSets



class DashboardView(APIView):

    def get(self, request):

        user = request.user

        # -------------------
        # ADMIN DASHBOARD
        # -------------------
        if user.is_staff:

            data = {
                "doctors": Doctor.objects.count(),
                "clinics": Clinic.objects.count(),
                "hospitals": Hospital.objects.count(),
                "labs": Lab.objects.count(),
                "appointments": Appointment.objects.count(),
                "lab_bookings": LabBooking.objects.count(),
            }

            return Response({"dashboard": "admin", "data": data})

        # -------------------
        # DOCTOR DASHBOARD
        # -------------------

        if user.user_type == "doctors":

            doctor = Doctor.objects.get(user=user)

            appointments = Appointment.objects.filter(doctor=doctor).count()

            return Response({
                "dashboard": "doctor",
                "data": {
                    "appointments": appointments,
                    "rating": doctor.ratings,
                }
            })

        # -------------------
        # HOSPITAL DASHBOARD
        # -------------------

        if user.user_type == "hospitals":

            hospital = Hospital.objects.get(user=user)

            return Response({
                "dashboard": "hospital",
                "data": {
                    "specialists": hospital.specialists.count(),
                }
            })

        # -------------------
        # CLINIC DASHBOARD
        # -------------------

        if user.user_type == "clincs":

            clinic = Clinic.objects.get(user=user)

            return Response({
                "dashboard": "clinic",
                "data": {
                    "specialists": clinic.specialists.count(),
                }
            })

        # -------------------
        # LAB DASHBOARD
        # -------------------

        if user.user_type == "labs":

            lab = Lab.objects.get(user=user)

            bookings = LabBooking.objects.filter(lab=lab).count()

            return Response({
                "dashboard": "lab",
                "data": {
                    "bookings": bookings
                }
            })
        

class AppointmentChartView(APIView):

    def get(self, request):

        qs = (
            Appointment.objects
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        return Response({
            "status": "success",
            "data": list(qs)
        })

class RecentAppointmentsView(APIView):

    def get(self, request):

        appointments = (
            Appointment.objects
            .select_related("patient")
            .order_by("-created_at")[:10]
        )

        data = []

        for a in appointments:
            data.append({
                "patient": a.patient.email,
                "created_at": a.created_at,
                "id": a.id
            })

        return Response({
            "status": "success",
            "data": data
        }) 
        

class EntitiesViewSet(TeriaqViewSets):
    """
    Generic viewset for all entities
    /dashboard/entities/<entity_type>/
    """

    def get_model(self, entity_type):

        mapping = {
            "hospitals": "hospitals.Hospital",
            "clincs": "clincs.Clinic",
            "doctors": "doctors.Doctor",
            "labs": "labs.Lab",
        }

        model_path = mapping.get(entity_type.lower())

        if not model_path:
            return None

        app_label, model_name = model_path.split(".")

        return apps.get_model(app_label, model_name)

    def get_queryset(self):

        entity_type = self.kwargs.get("entity_type")

        model = self.get_model(entity_type)

        if model is None:
            return model.objects.none()

        queryset = model.objects.all()

        if entity_type in ["hospitals", "clincs", "labs"]:
            queryset = queryset.prefetch_related(
                "specialists",
                "insurance",
                "certificates"
            ).select_related("about")

        return queryset

    def get_serializer_class(self):
        entity_type = self.kwargs.get("entity_type")
    
    # For doctors, use the dedicated DoctorSerializers
        if entity_type == "doctors":
            from doctors.serializers import DoctorSerializers
            return DoctorSerializers
    
    # For other entities (hospitals, clinics, labs), use dynamic EntitySerializer
        model = self.get_model(entity_type)
        if model is None:
            return None
    
        serializer_class = type(
            f"{entity_type.capitalize()}Serializer",
            (EntitySerializer,),
            {
                "Meta": type(
                    "Meta",
                    (),
                    {
                        "model": model,
                        "fields": "__all__"
                    }
                )
            }
        )
        return serializer_class

# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status
from django.contrib.auth.hashers import make_password
from accounts.models import User
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab
from doctors.models import Doctor, Specialist
from cloudinary.uploader import upload
import random
import string

class CreateEntityView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, entity_type):
        data = request.data
        user_data = {}
        entity_data = {}

        if entity_type == "doctors":
            # For doctors
            user_data = {
                'email': data.get('email'),
                'full_name': data.get('full_name'),
                'phone_number': data.get('phone_number'),
                'user_type': 'doctors',
            }
            entity_data = {
                'full_name': data.get('full_name'),
                'phone_number': data.get('phone_number'),
                'address': data.get('address'),
                'license_number': data.get('license_number'),
            }
            # Handle image uploads
            if data.get('profile_image'):
                entity_data['profile_image'] = self.upload_image(data['profile_image'])
            if data.get('license_document'):
                entity_data['license_document'] = self.upload_image(data['license_document'])
            # Get or create specialist
            specialist_name = data.get('specialist_name')
            if specialist_name:
                specialist, _ = Specialist.objects.get_or_create(name=specialist_name)
                entity_data['specialist'] = specialist
        else:
            # For hospitals, clinics, labs
            user_data = {
                'email': data.get('user_email'),
                'full_name': data.get('user_full_name'),
                'phone_number': data.get('user_phone'),
                'user_type': entity_type,  # 'hospitals', 'clincs', 'labs'
            }
            entity_data = {
                'name': data.get('name'),
                'address': data.get('address'),
                'phone': data.get('phone'),
                'email': data.get('email'),
                'description': data.get('description', ''),
            }
            if data.get('image'):
                entity_data['image'] = self.upload_image(data['image'])

        # Create user
        password = data.get('password') or self.generate_random_password()
        user_data['password'] = make_password(password)
        user = User.objects.create(**user_data)

        # Create entity
        if entity_type == "hospitals":
            entity = Hospital.objects.create(user=user, **entity_data)
        elif entity_type == "clincs":
            entity = Clinic.objects.create(user=user, **entity_data)
        elif entity_type == "labs":
            entity = Lab.objects.create(user=user, **entity_data)
        elif entity_type == "doctors":
            entity = Doctor.objects.create(user=user, **entity_data)
        else:
            user.delete()
            return Response({"error": "Invalid entity type"}, status=400)

        return Response({
            "message": f"{entity_type} created successfully",
            "user_id": user.id,
            "entity_id": entity.id,
            "password": password if not data.get('password') else None,
        }, status=201)


    def upload_image(self, base64_str):
        try:
            result = upload(base64_str)
            # Return the public ID instead of the full URL
            return result['public_id']
        except:
            return None

    def generate_random_password(self, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))