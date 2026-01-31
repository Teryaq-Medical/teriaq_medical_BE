from django.urls import include,path
from rest_framework import routers
from .views import HospitalViewSet

router = routers.DefaultRouter()
router.register(r'hospitals', HospitalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]