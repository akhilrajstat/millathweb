"""
apps/notices/admin.py
=====================
Django admin configuration for Notice model.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """
    Admin configuration for publishing and managing notices.
    """

    list_display = ("title", "category", "publish_date", "is_active", "created_at")
    list_filter = ("category", "is_active", "publish_date")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-publish_date", "-id")

    fieldsets = (
        (
            _("Notice Details"),
            {
                "fields": ("title", "slug", "category", "publish_date"),
                "description": _("Title, category tag, and official issue date."),
            },
        ),
        (
            _("Content & Documents"),
            {
                "fields": ("description", "file_attachment"),
                "description": _("Announcement text and optional attachment file (PDF/Word)."),
            },
        ),
        (
            _("Publication Controls"),
            {
                "fields": ("is_active",),
                "description": _("Toggle visibility on the public site."),
            },
        ),
    )
