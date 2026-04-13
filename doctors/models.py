from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from ASER.models import Biography, Certifications, Insurance
from specialists.models import Specialist
from cloudinary.models import CloudinaryField
from accounts.models import User



class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="doctor_profile"
    )

    full_name = models.CharField(max_length=100)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    license_number = models.CharField(max_length=100, unique=True)
    license_document = CloudinaryField("license")
    profile_image = CloudinaryField("image")
    
    insurance = models.ManyToManyField(Insurance, blank=True)
    certificates = models.ManyToManyField(Certifications, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    ratings = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class UnregisteredDoctor(models.Model):
    full_name = models.CharField(max_length=100)
    specialist = models.ForeignKey(Specialist, on_delete=models.CASCADE)

    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    profile_image = CloudinaryField("image")

    license_number = models.CharField(max_length=100)
    license_document = CloudinaryField("license")
    
    insurance = models.ManyToManyField(Insurance, blank=True)
    certificates = models.ManyToManyField(Certifications, blank=True)
    about = models.ForeignKey(Biography, on_delete=models.SET_NULL, null=True, blank=True)

    is_verified = models.BooleanField(default=False)

    ratings = models.IntegerField(default=0)

    allow_online_booking = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Admin approval for online booking"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class DoctorAssignment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("inactive", "Inactive"),
    )

    doctor = models.ForeignKey(
        Doctor,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    unregistered_doctor = models.ForeignKey(
        UnregisteredDoctor,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    entity = GenericForeignKey("content_type", "object_id")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="approved"  # GLOBAL doctors should be usable immediately
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(doctor__isnull=False, unregistered_doctor__isnull=True) |
                    models.Q(doctor__isnull=True, unregistered_doctor__isnull=False)
                ),
                name="only_one_doctor_source"
            )
        ]

    def __str__(self):
        doctor_name = self.doctor or self.unregistered_doctor

        if self.entity:
            return f"{self.entity} - {doctor_name}"

        return f"GLOBAL - {doctor_name}"


class WorkSchedule(models.Model):
    DAYS = [
        ("sat", "Saturday"),
        ("sun", "Sunday"),
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
    ]

    assignment = models.ForeignKey(
        DoctorAssignment,
        on_delete=models.CASCADE,
        related_name="schedules"
    )

    day = models.CharField(max_length=3, choices=DAYS)
    start_time = models.TimeField()
    date = models.DateField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.assignment} - {self.day}"
