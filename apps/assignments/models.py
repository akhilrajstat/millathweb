"""
apps/assignments/models.py
==========================
Data models for coursework assignments and student submissions.
"""

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from apps.accounts.models import UserRole
from apps.core.validators import validate_file_size_5mb


class Assignment(models.Model):
    """
    Academic coursework assignment created by faculty members.
    """

    title = models.CharField(
        _("assignment title"),
        max_length=255,
        help_text=_("Clear and descriptive title of the coursework assignment."),
    )
    description = CKEditor5Field(
        _("assignment instructions / description"),
        config_name="extends",
        help_text=_("Detailed guidelines, questions, rubric, and submission requirements."),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_assignments",
        limit_choices_to={"role": UserRole.FACULTY},
        verbose_name=_("faculty instructor"),
        help_text=_("Faculty member who created and oversees this assignment."),
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
        verbose_name=_("academic program"),
        help_text=_("Optionally restrict to an academic program / specialization. Leave empty for all students."),
    )
    due_date = models.DateTimeField(
        _("due date & time"),
        help_text=_("Strict submission deadline for students."),
    )
    max_marks = models.PositiveIntegerField(
        _("maximum marks"),
        default=100,
        help_text=_("Total maximum points or score achievable for this assignment."),
    )
    attachment = models.FileField(
        _("assignment attachment"),
        upload_to="assignments/attachments/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx"],
                message=_("Allowed file types are PDF, DOC, and DOCX."),
            ),
            validate_file_size_5mb,
        ],
        help_text=_("Optional reference document, rubric, or worksheet (PDF, DOC, DOCX up to 5MB)."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Toggle whether students can view and submit to this assignment."),
    )

    class Meta:
        verbose_name = _("Assignment")
        verbose_name_plural = _("Assignments")
        ordering = ["-due_date", "-created_at"]

    def __str__(self) -> str:
        prog = f" [{self.program.name}]" if self.program else " [All Programs]"
        return f"{self.title}{prog}"

    def get_absolute_url(self) -> str:
        return reverse("assignments:detail", kwargs={"pk": self.pk})

    @property
    def is_past_due(self) -> bool:
        """Returns True if the current time is past the assignment deadline."""
        return timezone.now() > self.due_date

    @property
    def total_submissions(self) -> int:
        """Total number of student submissions received."""
        return self.submissions.count()

    @property
    def graded_submissions_count(self) -> int:
        """Total number of submissions evaluated and graded."""
        return self.submissions.filter(marks_obtained__isnull=False).count()

    @property
    def pending_grading_count(self) -> int:
        """Submissions received that are waiting for faculty review and grading."""
        return self.submissions.filter(marks_obtained__isnull=True).count()


class Submission(models.Model):
    """
    Student coursework submission record for an assignment.
    """

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="submissions",
        verbose_name=_("assignment"),
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignment_submissions",
        limit_choices_to={"role": UserRole.STUDENT},
        verbose_name=_("student"),
    )
    submitted_file = models.FileField(
        _("submitted file"),
        upload_to="assignments/submissions/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "doc", "docx", "jpg", "jpeg", "png"],
                message=_("Allowed file formats are: PDF, DOC, DOCX, JPG, JPEG, and PNG."),
            ),
            validate_file_size_5mb,
        ],
        help_text=_("Upload your completed assignment file (Max 5MB; PDF, Word, or image)."),
    )
    submitted_at = models.DateTimeField(_("submitted at"), auto_now_add=True)
    marks_obtained = models.PositiveIntegerField(
        _("marks obtained"),
        null=True,
        blank=True,
        help_text=_("Awarded score evaluated by the instructor."),
    )
    feedback = models.TextField(
        _("instructor feedback"),
        blank=True,
        help_text=_("Evaluator commentary, constructive feedback, or suggestions."),
    )
    graded_at = models.DateTimeField(_("graded at"), null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graded_submissions",
        verbose_name=_("graded by"),
    )

    class Meta:
        verbose_name = _("Assignment Submission")
        verbose_name_plural = _("Assignment Submissions")
        ordering = ["-submitted_at"]
        unique_together = ("assignment", "student")

    def __str__(self) -> str:
        return f"{self.student.get_full_name() or self.student.username} - {self.assignment.title}"

    @property
    def is_graded(self) -> bool:
        """Returns True if the submission has been assigned marks."""
        return self.marks_obtained is not None

    @property
    def percentage(self) -> float | None:
        """Calculate score percentage based on maximum marks."""
        if self.marks_obtained is not None and self.assignment.max_marks:
            return round((self.marks_obtained / self.assignment.max_marks) * 100, 1)
        return None
