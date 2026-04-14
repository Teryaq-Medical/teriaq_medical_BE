from django.urls import include,path
from rest_framework import routers
from .views import LabsViewSets,LabSpecialistsViewSet

router = routers.DefaultRouter()
router.register(r'labs', LabsViewSets)
router.register(r'labs-specialists', LabSpecialistsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]