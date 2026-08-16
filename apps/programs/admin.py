"""
apps/programs/admin.py
======================
Django admin configuration for academic programs.
Tailored for non-technical office staff with photo previews, friendly help texts,
and Pillow-based image validation.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_image_file
from .models import Program


class ProgramAdminForm(forms.ModelForm):
    """Admin form for Program with friendly help texts and validation."""

    class Meta:
        model = Program
        fields = "__all__"
        help_texts = {
            "name": _("Full official title of the academic program (e.g. 'Bachelor of Education (B.Ed)')."),
            "slug": _("URL web-address identifier automatically generated from the course name. You can leave this unchanged."),
            "duration": _("Length and format of the program (e.g. '2 Years (4 Semesters)')."),
            "image": _("Upload a cover photo for this course card — landscape orientation works best, under 5MB."),
            "eligibility": _("State the minimum academic qualifications, cutoff marks, or subject prerequisites needed to apply."),
            "description": _("Detailed overview of the curriculum, objectives, career prospects, and program outcomes."),
            "syllabus_pdf": _("Optional: Upload the complete official syllabus or curriculum structure (PDF format only, under 5MB)."),
            "is_active": _("Check this box to show this program on the public website. Uncheck to hide it from visitors."),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "file"):
            validate_image_file(image)
        return image


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """
    Admin interface for managing academic degrees, teacher training courses, and syllabi.
    """

    form = ProgramAdminForm
    list_display = ("thumbnail_preview", "name", "duration", "has_syllabus", "is_active", "created_at")
    list_display_links = ("thumbnail_preview", "name")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "eligibility")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("image_preview",)

    fieldsets = (
        (
            _("Program Overview & Cover Photo"),
            {
                "fields": ("name", "slug", "duration", "image", "image_preview"),
                "description": _("Enter the course name, duration, and upload an attractive cover photo for the course card."),
            },
        ),
        (
            _("Curriculum & Admission Details"),
            {
                "fields": ("eligibility", "description", "syllabus_pdf"),
                "description": _("Specify eligibility requirements, curriculum overview, and upload the downloadable syllabus PDF."),
            },
        ),
        (
            _("Website Visibility"),
            {
                "fields": ("is_active",),
                "description": _("Toggle whether this course is currently displayed to students and prospective applicants."),
            },
        ),
    )

    @admin.display(description=_("Cover Photo"))
    def thumbnail_preview(self, obj: Program):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 70px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" />',
                obj.image.url,
                obj.name,
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">No cover</span>')

    @admin.display(description=_("Syllabus"))
    def has_syllabus(self, obj: Program):
        if obj.syllabus_pdf:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0284c7; font-weight: 500; text-decoration: none;" title="Download Syllabus">📄 PDF</a>',
                obj.syllabus_pdf.url,
            )
        return format_html('<span style="color: #94a3b8;">—</span>')

    @admin.display(description=_("Current Cover Photo Preview"))
    def image_preview(self, obj: Program):
        if obj and obj.image:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="{}" style="max-width: 100%; max-height: 220px; object-fit: cover; border-radius: 6px; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.image.url,
                obj.name,
            )
        return _("Upload a cover photo above to see a preview.")
