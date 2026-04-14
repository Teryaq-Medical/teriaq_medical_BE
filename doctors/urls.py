from django.urls import include, path
from rest_framework import routers
from .views import DoctorsViewSet, WorkScheduleViewSet, UnregisteredDoctorsViewSet,DoctorAssignmentViewSet

router = routers.DefaultRouter()
router.register(r'doctors', DoctorsViewSet, basename='doctors')
router.register(r'un-doctors', UnregisteredDoctorsViewSet, basename='unregistered-doctors')
router.register(r'work-schedule', WorkScheduleViewSet, basename='date-time')
router.register(r'doctor-assignments', DoctorAssignmentViewSet, basename='assignments')

urlpatterns = [
    path('', include(router.urls)),
]