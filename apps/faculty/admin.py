"""
apps/faculty/admin.py
=====================
Django admin configuration for FacultyProfile.
Tailored for non-technical office staff with photo previews, friendly help texts,
and Pillow-based image validation.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_image_file
from .models import FacultyProfile


class FacultyProfileAdminForm(forms.ModelForm):
    """Admin form for FacultyProfile with friendly guidance and image validation."""

    class Meta:
        model = FacultyProfile
        fields = "__all__"
        help_texts = {
            "user": _("Select the staff/faculty member user account this profile belongs to."),
            "designation": _("Official academic or administrative title (e.g. 'Principal', 'Assistant Professor in Education')."),
            "qualification": _("Degrees and academic credentials (e.g. 'M.Ed., M.Phil., Ph.D., NET')."),
            "specialization": _("Subject expertise or primary department (e.g. 'Pedagogy of English', 'Educational Psychology')."),
            "email_display": _("Public email displayed on the faculty directory for student queries (leave blank to use account email)."),
            "photo": _("Upload a professional passport-style or portrait photograph (under 5MB)."),
            "bio": _("Detailed biography, research publications, awards, and teaching experience."),
            "display_order": _("Order on the public Faculty Directory page (lower numbers like 0, 1 appear first)."),
            "is_published": _("Check this box to show this faculty profile on the public website."),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "file"):
            validate_image_file(photo)
        return photo


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing public faculty profiles and directory.
    """

    form = FacultyProfileAdminForm
    list_display = (
        "photo_thumbnail",
        "get_full_name",
        "designation",
        "qualification",
        "specialization",
        "display_order",
        "is_published",
    )
    list_display_links = ("photo_thumbnail", "get_full_name")
    list_editable = ("display_order", "is_published")
    list_filter = ("is_published", "designation")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "designation",
        "qualification",
        "specialization",
    )
    ordering = ("display_order", "user__first_name")
    readonly_fields = ("photo_preview",)

    fieldsets = (
        (
            _("Faculty User Account"),
            {
                "fields": ("user",),
                "description": _("Associate this public profile with an existing faculty login account."),
            },
        ),
        (
            _("Academic Designation & Credentials"),
            {
                "fields": (
                    "designation",
                    "qualification",
                    "specialization",
                    "email_display",
                ),
                "description": _("Official academic title, qualifications, and public contact email."),
            },
        ),
        (
            _("Portrait Photo"),
            {
                "fields": ("photo", "photo_preview"),
                "description": _("Upload a clean, professional portrait or passport photo for the directory."),
            },
        ),
        (
            _("Detailed Biography & Experience"),
            {
                "fields": ("bio",),
                "description": _("Detailed curriculum vitae, research publications, teaching history, and awards."),
            },
        ),
        (
            _("Website Display Settings"),
            {
                "fields": ("display_order", "is_published"),
                "description": _("Control display sequence (lower numbers first) and publication status on the public website."),
            },
        ),
    )

    @admin.display(description=_("Photo"))
    def photo_thumbnail(self, obj: FacultyProfile):
        if obj and obj.photo:
            return format_html(
                '<img src="{}" alt="{}" style="width: 40px; height: 40px; border-radius: 50%; object-fit: cover; border: 1px solid #cbd5e1;" />',
                obj.photo.url,
                obj.full_name,
            )
        return format_html(
            '<div style="width: 40px; height: 40px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 11px; font-weight: 600;">{}</div>',
            (obj.full_name[:2] if obj.full_name else "FP").upper(),
        )

    @admin.display(description=_("Faculty Name"), ordering="user__first_name")
    def get_full_name(self, obj: FacultyProfile) -> str:
        return obj.full_name

    @admin.display(description=_("Current Photo Preview"))
    def photo_preview(self, obj: FacultyProfile):
        if obj and obj.photo:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="{}" style="max-height: 180px; max-width: 180px; object-fit: cover; border-radius: 8px; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.photo.url,
                obj.full_name,
            )
        return _("Upload a photo above to see a preview.")
