from django.db import models
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField
from specialists.models import Specialist
from accounts.models import User
from ASER.models import BaseMedicalEntity


class Clinic(BaseMedicalEntity):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    specialists = models.ManyToManyField(Specialist)

    def __str__(self):
        return self.name

