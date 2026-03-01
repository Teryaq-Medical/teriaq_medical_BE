from django.db import models
from cloudinary.models import CloudinaryField
from accounts.models import User
from specialists.models import Specialist
from ASER.models import BaseMedicalEntity

class Hospital(BaseMedicalEntity):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    specialists = models.ManyToManyField(Specialist)

    def __str__(self):
        return self.name

