from .models import Insurance, Certifications, Biography
from .viewset import TeriaqViewSets
from .serializers import InsuranceSerializer, CertificationsSerializer, BiographySerializer
from .permissions import IsAdminOrMedicalEntity
from hospitals.models import Hospital
from clincs.models import Clinic
from labs.models import Lab

ENTITY_MODELS = {
    "hospitals": Hospital,
    "clinics": Clinic,
    "labs": Lab,
}


# ----------------------------
# 🔹 Insurance ViewSet
# ----------------------------
class InsuranceViewSet(TeriaqViewSets):
    serializer_class = InsuranceSerializer
    permission_classes = [IsAdminOrMedicalEntity]

    def get_queryset(self):
        entity_type = self.kwargs.get("entity_type")
        entity_id = self.kwargs.get("entity_id")

        entity_model = ENTITY_MODELS.get(entity_type)
        if not entity_model:
            return Insurance.objects.none()

        entity = entity_model.objects.filter(id=entity_id).first()
        if not entity:
            return Insurance.objects.none()

        return entity.insurance.all()


# ----------------------------
# 🔹 Certifications ViewSet
# ----------------------------
class CertificationsViewSet(TeriaqViewSets):
    serializer_class = CertificationsSerializer
    permission_classes = [IsAdminOrMedicalEntity]

    def get_queryset(self):
        entity_type = self.kwargs.get("entity_type")
        entity_id = self.kwargs.get("entity_id")

        entity_model = ENTITY_MODELS.get(entity_type)
        if not entity_model:
            return Certifications.objects.none()

        entity = entity_model.objects.filter(id=entity_id).first()
        if not entity:
            return Certifications.objects.none()

        return entity.certificates.all()


# ----------------------------
# 🔹 Biography ViewSet
# ----------------------------
class BiographyViewSet(TeriaqViewSets):
    serializer_class = BiographySerializer
    permission_classes = [IsAdminOrMedicalEntity]

    def get_queryset(self):
        entity_type = self.kwargs.get("entity_type")
        entity_id = self.kwargs.get("entity_id")

        entity_model = ENTITY_MODELS.get(entity_type)
        if not entity_model:
            return Biography.objects.none()

        entity = entity_model.objects.filter(id=entity_id).first()
        if not entity or not entity.about:
            return Biography.objects.none()

        return Biography.objects.filter(id=entity.about.id)
