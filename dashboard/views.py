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

        model = self.get_model(entity_type)

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