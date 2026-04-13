from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.urls import path
from .views import InsuranceViewSet, CertificationsViewSet, BiographyViewSet



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('clincs.urls')),
    path('api/', include('doctors.urls')),
    path('api/', include('hospitals.urls')),
    path('api/', include('labs.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('appointments.urls')),
    path("api/dashboard/", include("dashboard.urls")),
    path('api/', include('entities.urls')),
    path('api/<str:entity_type>/<int:entity_id>/insurance/', InsuranceViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/<str:entity_type>/<int:entity_id>/certifications/', CertificationsViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/<str:entity_type>/<int:entity_id>/bio/', BiographyViewSet.as_view({'get': 'list', 'post': 'create'})),  # <-- moved here
]
