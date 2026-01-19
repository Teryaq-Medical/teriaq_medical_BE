from django.urls import include,path
from rest_framework import routers
from .views import ClincsViewSet

router = routers.DefaultRouter()
router.register(r'clincs', ClincsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]