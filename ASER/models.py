from django.db import models
from cloudinary.models import CloudinaryField


# ASER/models.py

from django.db import models
from accounts.models import User


class Biography(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=25)
    bio_details = models.TextField(max_length=100)
    experiance = models.IntegerField()
    operaiton = models.IntegerField()

    def __str__(self):
        return f"Biography - {self.created_by}"


class Certifications(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.TextField(max_length=80)
    entity = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Insurance(models.Model):
    FULL_COVERAGE = 'تغطية كاملة'
    STANDARD = 'عادية'
    PARTIAL = 'جزئية'
    EXPIRED = 'منتهية'

    STATUS_CHOICES = [
        (FULL_COVERAGE, 'تغطية كاملة'),
        (STANDARD, 'عادية'),
        (PARTIAL, 'جزئية'),
        (EXPIRED, 'منتهية'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    entity = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STANDARD
    )

    def __str__(self):
        return f"{self.entity} ({self.get_status_display()})"


class BaseMedicalEntity(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    image = CloudinaryField("image")

    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )
    
    insurance = models.ManyToManyField(Insurance,null=True,blank=True)
    certificates = models.ManyToManyField(Certifications,null=True,blank=True)
    about = models.ForeignKey(Biography,on_delete=models.CASCADE,null=True,blank=True)

    facebook_url = models.URLField(blank=True, null=True)
    x_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True
