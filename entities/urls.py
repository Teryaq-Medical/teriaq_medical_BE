# entities/urls.py

from django.urls import path
from .views import (
    EntityUpdateView,
    EntityAboutUpdateView,
    EntityInsuranceView,
    EntityCertificateView,
    EntitySpecialistView,
    EntityDoctorAssignmentView,
)

urlpatterns = [
    # Basic info update
    path('api/entities/<str:entity_type>/<int:id>/update/', 
         EntityUpdateView.as_view(), name='entity-update'),
    
    # About update
    path('api/entities/<str:entity_type>/<int:id>/about/update/', 
         EntityAboutUpdateView.as_view(), name='entity-about-update'),
    
    # Insurance management
    path('api/entities/<str:entity_type>/<int:id>/insurance/add/', 
         EntityInsuranceView.as_view(), name='entity-insurance-add'),
    path('api/entities/<str:entity_type>/<int:id>/insurance/<int:insurance_id>/remove/', 
         EntityInsuranceView.as_view(), name='entity-insurance-remove'),
    
    # Certificate management
    path('api/entities/<str:entity_type>/<int:id>/certificate/add/', 
         EntityCertificateView.as_view(), name='entity-certificate-add'),
    path('api/entities/<str:entity_type>/<int:id>/certificate/<int:cert_id>/remove/', 
         EntityCertificateView.as_view(), name='entity-certificate-remove'),
    
    # Specialist management
    path('api/entities/<str:entity_type>/<int:id>/specialist/add/', 
         EntitySpecialistView.as_view(), name='entity-specialist-add'),
    path('api/entities/<str:entity_type>/<int:id>/specialist/<int:specialist_id>/remove/', 
         EntitySpecialistView.as_view(), name='entity-specialist-remove'),
    
    # Doctor assignment management
    path('api/entities/<str:entity_type>/<int:id>/doctor/add/', 
         EntityDoctorAssignmentView.as_view(), name='entity-doctor-add'),
    path('api/entities/<str:entity_type>/<int:id>/doctor/<int:assignment_id>/remove/', 
         EntityDoctorAssignmentView.as_view(), name='entity-doctor-remove'),
]