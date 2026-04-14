import uuid
from django.db import models
from doctors.models import DoctorAssignment, WorkSchedule
from accounts.models import User
from labs.models import Lab

def generate_booking_code():
    return str(uuid.uuid4()).split("-")[0].upper()


class Appointment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    )

    assignment = models.ForeignKey(
        DoctorAssignment,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    schedule = models.ForeignKey(
        WorkSchedule,
        on_delete=models.CASCADE
    )

    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    
    booking_code = models.CharField(
        max_length=20,
        unique=True,
        default=generate_booking_code,
        editable=False
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "schedule",
            "appointment_date",
            "appointment_time",
        )

    def __str__(self):
        return f"{self.patient} → {self.assignment}"
    
    

def generate_lab_booking_code():
    return str(uuid.uuid4()).split("-")[0].upper()

class LabBooking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="lab_bookings")
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name="lab_bookings")
    service_name = models.CharField(max_length=255)
    booking_code = models.CharField(max_length=20, unique=True, default=generate_lab_booking_code, editable=False)
    status = models.CharField(max_length=20, choices=[
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled")
    ], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient} → Lab: {self.lab} {self.booking_code}"
