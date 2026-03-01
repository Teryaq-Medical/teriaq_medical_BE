from django.contrib import admin
from .models import Appointment,LabBooking

admin.site.register(LabBooking)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "patient",
        "assignment",
        "appointment_date",
        "appointment_time",
        "booking_code",
        "status",
    )

    readonly_fields = (
        "booking_code",
        "created_at",
    )

    search_fields = (
        "booking_code",
        "patient__email",
    )

    list_filter = (
        "status",
        "appointment_date",
    )
