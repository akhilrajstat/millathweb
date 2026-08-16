"""
apps/programs/admin.py
======================
Django admin configuration for academic programs.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """
    Admin interface for managing academic degrees and courses.
    """

    list_display = ("name", "duration", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description", "eligibility")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)

    fieldsets = (
        (
            _("Program Overview"),
            {
                "fields": ("name", "slug", "duration", "image"),
                "description": _("Title, URL slug, duration, and promotional image."),
            },
        ),
        (
            _("Curriculum & Admission Details"),
            {
                "fields": ("eligibility", "description", "syllabus_pdf"),
                "description": _("Rich text course description, eligibility requirements, and downloadable syllabus."),
            },
        ),
        (
            _("Visibility Status"),
            {
                "fields": ("is_active",),
            },
        ),
    )
