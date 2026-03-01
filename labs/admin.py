from django.contrib import admin
from django.utils.html import format_html
from .models import Lab,LabSpecialists

admin.site.register(LabSpecialists)

@admin.register(Lab)
class LabsAdmin(admin.ModelAdmin):
    # ===== LIST VIEW =====
    list_display = (
        'user',
        'name',
        'get_specialists',  # <-- changed
        'image_preview',
        'address',
        'phone',
        'email',
        'rating',
    )

    list_filter = ('user',)
    search_fields = ('user__full_name', 'name')

    # ===== READONLY =====
    readonly_fields = ('image_preview',)

    # ===== FORM LAYOUT =====
    fieldsets = (
        ("المعلومات الأساسية", {
            'fields': (
                'user',
                'name',
                'specialists',
                'about',
                'insurance',
                'certificates',
                'address',
                'phone',
                'email',
                'rating',
            )
        }),
        ("الصور", {
            'fields': ('image', 'image_preview'),
        }),
    )

    # ===== METHODS =====

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="100" height="100" '
                'style="border-radius:10px; object-fit:cover; border:1px solid #ddd;" />',
                obj.image.url
            )
        return "—"

    image_preview.short_description = "معاينة الصورة"

    def get_specialists(self, obj):
        return ", ".join([s.name for s in obj.specialists.all()])
    get_specialists.short_description = "الأخصائيون"
