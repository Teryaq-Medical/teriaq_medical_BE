from django.contrib import admin
from django.utils.html import format_html
from .models import Clincs

@admin.register(Clincs)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'clinic_image')
    list_filter = ('user',)
    search_fields = ('user__username', 'name', 'Specialist__name')

    readonly_fields = ('clinic_image',)  # <-- Make it appear in detail page

    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'Specialist', 'image', 'clinic_image')  # add clinic_image here
        }),
    )

    def clinic_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" height="60" style="border-radius:8px; object-fit:cover;" />',
                obj.image.url
            )
        return "—"

    clinic_image.short_description = "الصورة"
