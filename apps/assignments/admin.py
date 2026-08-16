"""
apps/assignments/admin.py
=========================
Django administration integration for Assignments and Student Submissions.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.assignments.models import Assignment, Submission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "program_display",
        "created_by",
        "due_date",
        "max_marks",
        "is_active",
        "submissions_status",
        "created_at",
    ]
    list_filter = ["is_active", "program", "due_date", "created_at"]
    search_fields = [
        "title",
        "description",
        "created_by__first_name",
        "created_by__last_name",
        "created_by__username",
    ]
    raw_id_fields = ["created_by"]
    date_hierarchy = "due_date"
    ordering = ["-due_date"]

    @admin.display(description=_("Program / Scope"))
    def program_display(self, obj):
        if obj.program:
            return obj.program.name
        return format_html("<span style='color: #666;'>{}</span>", _("All Programs"))

    @admin.display(description=_("Submissions / Graded"))
    def submissions_status(self, obj):
        total = obj.total_submissions
        graded = obj.graded_submissions_count
        return format_html(
            "<strong>{}</strong> total ({} graded)",
            total,
            graded,
        )


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "assignment",
        "submitted_at",
        "marks_status",
        "graded_by",
        "graded_at",
    ]
    list_filter = [
        "assignment__program",
        "submitted_at",
        "graded_at",
    ]
    search_fields = [
        "student__first_name",
        "student__last_name",
        "student__username",
        "student__email",
        "assignment__title",
        "feedback",
    ]
    raw_id_fields = ["assignment", "student", "graded_by"]
    readonly_fields = ["submitted_at"]
    ordering = ["-submitted_at"]

    @admin.display(description=_("Score / Evaluation"))
    def marks_status(self, obj):
        if obj.marks_obtained is not None:
            pct = obj.percentage
            return format_html(
                "<span style='color: green; font-weight: bold;'>{}/{} ({}%)</span>",
                obj.marks_obtained,
                obj.assignment.max_marks,
                pct,
            )
        return format_html("<span style='color: #c98800; font-weight: 500;'>{}</span>", _("Pending Grading"))
