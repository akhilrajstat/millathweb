"""
apps/faculty/admin.py
=====================
Django admin configuration for FacultyProfile.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import FacultyProfile


@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing public faculty profiles.
    """

    list_display = (
        "get_full_name",
        "designation",
        "qualification",
        "specialization",
        "display_order",
        "is_published",
    )
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

    fieldsets = (
        (
            _("User Account"),
            {
                "fields": ("user",),
                "description": _("Associate this profile with an active faculty user account."),
            },
        ),
        (
            _("Academic Credentials & Role"),
            {
                "fields": (
                    "designation",
                    "qualification",
                    "specialization",
                    "email_display",
                    "photo",
                ),
                "description": _("Public-facing academic titles, qualifications, and portrait photograph."),
            },
        ),
        (
            _("Detailed Biography"),
            {
                "fields": ("bio",),
                "description": _("Detailed curriculum vitae, research publications, teaching history, and awards."),
            },
        ),
        (
            _("Publishing Status"),
            {
                "fields": ("display_order", "is_published"),
                "description": _("Control display sequence and publication status on the public website."),
            },
        ),
    )

    @admin.display(description=_("Faculty Name"), ordering="user__first_name")
    def get_full_name(self, obj: FacultyProfile) -> str:
        return obj.full_name
