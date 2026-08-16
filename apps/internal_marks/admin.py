"""
apps/internal_marks/admin.py
============================
Django Admin configuration for InternalMark model (read-only audit & oversight).
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.internal_marks.models import InternalMark, MarkStatus


@admin.register(InternalMark)
class InternalMarkAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "program",
        "subject",
        "marks_display",
        "status_badge",
        "entered_by",
        "reviewed_by",
        "published_at",
    ]
    list_filter = ["status", "program", "entered_at", "published_at"]
    search_fields = [
        "student__username",
        "student__first_name",
        "student__last_name",
        "student__email",
        "subject",
        "entered_by__username",
        "entered_by__first_name",
        "entered_by__last_name",
    ]
    raw_id_fields = ["student", "program", "entered_by", "reviewed_by"]
    readonly_fields = [
        "student",
        "program",
        "subject",
        "max_marks",
        "marks_obtained",
        "entered_by",
        "entered_at",
        "status",
        "reviewed_by",
        "reviewed_at",
        "review_comment",
        "published_at",
    ]
    ordering = ["-entered_at"]

    @admin.display(description=_("Marks Awarded"))
    def marks_display(self, obj):
        pct = obj.percentage
        return format_html(
            "<strong>{}/{}</strong> ({}%)",
            obj.marks_obtained,
            obj.max_marks,
            pct,
        )

    @admin.display(description=_("Status"))
    def status_badge(self, obj):
        colors = {
            MarkStatus.DRAFT: "#6c757d",
            MarkStatus.SUBMITTED: "#ffc107",
            MarkStatus.APPROVED: "#0d6efd",
            MarkStatus.REJECTED: "#dc3545",
            MarkStatus.PUBLISHED: "#198754",
        }
        color = colors.get(obj.status, "#6c757d")
        text_color = "#000" if obj.status == MarkStatus.SUBMITTED else "#fff"
        return format_html(
            "<span style='background-color: {}; color: {}; padding: 3px 8px; border-radius: 4px; font-weight: 600; font-size: 0.8rem;'>{}</span>",
            color,
            text_color,
            obj.get_status_display(),
        )
