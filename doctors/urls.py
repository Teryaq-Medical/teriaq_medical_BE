from django.urls import include,path
from rest_framework import routers
from .views import DoctorsViewSet

router = routers.DefaultRouter()
router.register(r'doctors', DoctorsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]