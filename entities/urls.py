# entities/urls.py

from django.urls import path
from .views import (
    EntityUpdateView,
    EntityAboutUpdateView,
    EntityInsuranceView,
    EntityCertificateView,
    EntitySpecialistView,
    EntityDoctorAssignmentView,
    DoctorSpecialistView,
    DoctorScheduleView,
    DoctorCertificateView,
    DoctorInsuranceView,
)

urlpatterns = [
    # ========== ENTITY-SPECIFIC ENDPOINTS ==========
    path('entities/<str:entity_type>/<int:id>/update/',
         EntityUpdateView.as_view(), name='entity-update'),
    path('entities/<str:entity_type>/<int:id>/about/update/',
         EntityAboutUpdateView.as_view(), name='entity-about-update'),
    path('entities/<str:entity_type>/<int:id>/insurance/add/',
         EntityInsuranceView.as_view(), name='entity-insurance-add'),
    path('entities/<str:entity_type>/<int:id>/insurance/<int:insurance_id>/remove/',
         EntityInsuranceView.as_view(), name='entity-insurance-remove'),
    path('entities/<str:entity_type>/<int:id>/certificate/add/',
         EntityCertificateView.as_view(), name='entity-certificate-add'),
    path('entities/<str:entity_type>/<int:id>/certificate/<int:cert_id>/remove/',
         EntityCertificateView.as_view(), name='entity-certificate-remove'),
    path('entities/<str:entity_type>/<int:id>/specialist/add/',
         EntitySpecialistView.as_view(), name='entity-specialist-add'),
    path('entities/<str:entity_type>/<int:id>/specialist/<int:specialist_id>/remove/',
         EntitySpecialistView.as_view(), name='entity-specialist-remove'),
    path('entities/<str:entity_type>/<int:id>/doctor/add/',
         EntityDoctorAssignmentView.as_view(), name='entity-doctor-add'),
    path('entities/<str:entity_type>/<int:id>/doctor/<int:assignment_id>/remove/',
         EntityDoctorAssignmentView.as_view(), name='entity-doctor-remove'),

    # ========== DOCTOR-SPECIFIC ENDPOINTS ==========
    path('doctors/<int:doctor_id>/specialist/update/',
         DoctorSpecialistView.as_view(), name='doctor-specialist-update'),
    path('doctors/<int:doctor_id>/schedule/add/',
         DoctorScheduleView.as_view(), name='doctor-schedule-add'),
    path('doctors/<int:doctor_id>/schedule/<int:schedule_id>/remove/',
         DoctorScheduleView.as_view(), name='doctor-schedule-remove'),
    path('doctors/<int:doctor_id>/schedule/<int:schedule_id>/update/',
         DoctorScheduleView.as_view(), name='doctor-schedule-update'),
    path('doctors/<int:doctor_id>/certificate/add/',
         DoctorCertificateView.as_view(), name='doctor-certificate-add'),
    path('doctors/<int:doctor_id>/certificate/<int:cert_id>/remove/',
         DoctorCertificateView.as_view(), name='doctor-certificate-remove'),
    path('doctors/<int:doctor_id>/insurance/add/',
         DoctorInsuranceView.as_view(), name='doctor-insurance-add'),
    path('doctors/<int:doctor_id>/insurance/<int:insurance_id>/remove/',
         DoctorInsuranceView.as_view(), name='doctor-insurance-remove'),
]