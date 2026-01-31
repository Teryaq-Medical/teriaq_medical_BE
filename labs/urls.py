from django.urls import include,path
from rest_framework import routers
from .views import LabsViewSets

router = routers.DefaultRouter()
router.register(r'labs', LabsViewSets)

urlpatterns = [
    path('', include(router.urls)),
]