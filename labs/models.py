from django.db import models
from accounts.models import User
from ASER.models import BaseMedicalEntity
from cloudinary.models import CloudinaryField

class LabSpecialists(models.Model):
    name = models.CharField(max_length=50)
    image = CloudinaryField("image")

class Lab(BaseMedicalEntity):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialists = models.ManyToManyField(LabSpecialists, related_name="labs")

    def __str__(self):
        return self.name