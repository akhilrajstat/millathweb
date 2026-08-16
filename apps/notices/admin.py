"""
apps/notices/admin.py
=====================
Django admin configuration for Notice model.
Tailored for non-technical office staff with friendly help text, clear sectioning,
and intuitive status indicators.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Notice


class NoticeAdminForm(forms.ModelForm):
    """Admin form for Notice with plain-English help texts and guidance."""

    class Meta:
        model = Notice
        fields = "__all__"
        help_texts = {
            "title": _("Enter a clear, concise headline for the notice (e.g. 'Semester II Examination Schedule Announced')."),
            "slug": _("Automatically generated web-address shortcut from the title. You can leave this unchanged."),
            "category": _("Select the category that best matches this announcement so students can filter it easily."),
            "description": _("Write the full notice details, instructions, dates, or guidelines using the rich text editor."),
            "file_attachment": _("Optional: Upload an official circular or form (PDF format only, under 5MB)."),
            "publish_date": _("The official publication date displayed on the circular (defaults to today)."),
            "is_active": _("Check this box to make the notice visible on the website. Uncheck to save as draft or archive."),
        }


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """
    Admin configuration for publishing and managing college notices and circulars.
    """

    form = NoticeAdminForm
    list_display = ("title", "category_badge", "has_attachment", "publish_date", "is_active", "created_at")
    list_filter = ("category", "is_active", "publish_date")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-publish_date", "-id")

    fieldsets = (
        (
            _("Notice Heading & Category"),
            {
                "fields": ("title", "slug", "category", "publish_date"),
                "description": _("Provide the main notice title, select its category, and confirm the official issue date."),
            },
        ),
        (
            _("Notice Content & Document Attachment"),
            {
                "fields": ("description", "file_attachment"),
                "description": _("Compose the announcement body below and attach an optional official PDF circular if applicable."),
            },
        ),
        (
            _("Publishing Status"),
            {
                "fields": ("is_active",),
                "description": _("Turn this switch ON to publish immediately to students and faculty, or OFF to keep hidden."),
            },
        ),
    )

    @admin.display(description=_("Category"), ordering="category")
    def category_badge(self, obj: Notice):
        badge_colors = {
            "general": "#475569",
            "academic": "#0284c7",
            "exam": "#dc2626",
            "admission": "#059669",
            "event": "#7c3aed",
        }
        color = badge_colors.get(obj.category, "#475569")
        return format_html(
            '<span style="background-color: {}; color: #ffffff; padding: 3px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; white-space: nowrap;">{}</span>',
            color,
            obj.get_category_display(),
        )

    @admin.display(description=_("PDF Circular"))
    def has_attachment(self, obj: Notice):
        if obj.file_attachment:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0284c7; font-weight: 500; text-decoration: none;" title="Open PDF">📄 View PDF</a>',
                obj.file_attachment.url,
            )
        return format_html('<span style="color: #94a3b8;">—</span>')
