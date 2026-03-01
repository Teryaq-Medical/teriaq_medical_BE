from django.contrib import admin
from django.utils.html import format_html
from .models import Doctor,UnregisteredDoctor,WorkSchedule,DoctorAssignment


admin.site.register(UnregisteredDoctor)
admin.site.register(WorkSchedule)
admin.site.register(DoctorAssignment)
@admin.register(Doctor)
class DoctorsAdmin(admin.ModelAdmin):
    # 1. Columns in the main list view
    list_display = ('user', 'full_name', 'phone_number', 'license_document_url', 'profile_image_url', 'address', 'specialist','is_verified','license_number')
    list_filter = ('user',)
    search_fields = ('user__full_name', 'name', 'specialist__name')

    # 2. CRITICAL: Add both methods here so they can appear in the detail page
    readonly_fields = ('license_document_url', 'profile_image_url')

    # 3. Organize the edit page
    fieldsets = (
        ("المعلومات الأساسية", {
            'fields': ('user', 'full_name', 'phone_number', 'address', 'specialist','is_verified','license_number')
        }),
        ("الصور والوثائق", {
            'fields': (
                'profile_image', 'profile_image_url',  # Upload field + Preview
                'license_document', 'license_document_url'           # Upload field + Preview
            )
        }),
    )

    # --- Custom Preview Methods ---

    def profile_image_url(self, obj):
        if obj.profile_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:8px; object-fit:cover; border:1px solid #ddd;" />',
                obj.profile_image.url
            )
        return "—"
    profile_image_url.short_description = "معاينة صورة الطبيب"

    def license_document_url(self, obj):
        if obj.license_document:
            return format_html(
                '<img src="{}" width="100" height="100" style="border-radius:8px; object-fit:cover; border:1px solid #ddd;" />',
                obj.license_document.url
            )
        return "—"
    license_document_url.short_description = "معاينة رخصة العمل"