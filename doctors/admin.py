from django.contrib import admin
from django.utils.html import format_html
from .models import Doctors

@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    # 1. Columns in the main list view
    list_display = ('user', 'name', 'age', 'phone_number', 'license_image', 'doctor_image_url', 'address', 'specialist')
    list_filter = ('user',)
    search_fields = ('user__full_name', 'name', 'specialist__name')

    # 2. CRITICAL: Add both methods here so they can appear in the detail page
    readonly_fields = ('license_image', 'doctor_image_url')

    # 3. Organize the edit page
    fieldsets = (
        ("المعلومات الأساسية", {
            'fields': ('user', 'name', 'age', 'phone_number', 'address', 'specialist')
        }),
        ("الصور والوثائق", {
            'fields': (
                'doctor_image', 'doctor_image_url',  # Upload field + Preview
                'license', 'license_image'           # Upload field + Preview
            )
        }),
    )

    # --- Custom Preview Methods ---

    def doctor_image_url(self, obj):
        if obj.doctor_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:8px; object-fit:cover; border:1px solid #ddd;" />',
                obj.doctor_image.url
            )
        return "—"
    doctor_image_url.short_description = "معاينة صورة الطبيب"

    def license_image(self, obj):
        if obj.license:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:8px; object-fit:cover; border:1px solid #ddd;" />',
                obj.license.url
            )
        return "—"
    license_image.short_description = "معاينة رخصة العمل"