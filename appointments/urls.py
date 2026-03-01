# appointments/urls.py
from django.urls import include, path
from rest_framework import routers
from .views import AppointmentViewSet,LabBookingViewSet

router = routers.DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")
router.register(r"lab-bookings", LabBookingViewSet, basename="lab-booking")

urlpatterns = [
    path("", include(router.urls)),
]
