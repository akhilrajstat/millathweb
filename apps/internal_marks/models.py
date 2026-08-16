"""
apps/internal_marks/models.py
=============================
Data models and multi-stage workflow status definitions for internal assessment marks.
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole


class MarkStatus(models.TextChoices):
    """
    State machine choices for the internal mark evaluation and publishing lifecycle.
    """

    DRAFT = "draft", _("Draft")
    SUBMITTED = "submitted", _("Submitted for Review")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")
    PUBLISHED = "published", _("Published")


class InternalMark(models.Model):
    """
    Internal continuous assessment mark record for a student in a specific course/subject.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="internal_marks",
        limit_choices_to={"role": UserRole.STUDENT},
        verbose_name=_("student"),
        help_text=_("Student receiving this internal evaluation score."),
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.PROTECT,
        related_name="internal_marks",
        verbose_name=_("academic program"),
        help_text=_("Academic degree program or specialization."),
    )
    subject = models.CharField(
        _("course / subject name"),
        max_length=200,
        help_text=_("Course title or subject component (e.g., 'Pedagogy of Mathematics', 'ICT in Education')."),
    )
    max_marks = models.PositiveIntegerField(
        _("maximum marks"),
        default=20,
        help_text=_("Maximum achievable score for this internal assessment."),
    )
    marks_obtained = models.PositiveIntegerField(
        _("marks obtained"),
        help_text=_("Score awarded to the student."),
    )
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entered_internal_marks",
        limit_choices_to={"role": UserRole.FACULTY},
        verbose_name=_("evaluating faculty"),
        help_text=_("Faculty instructor who evaluated and entered these marks."),
    )
    entered_at = models.DateTimeField(_("entered at"), auto_now_add=True)
    status = models.CharField(
        _("approval status"),
        max_length=20,
        choices=MarkStatus.choices,
        default=MarkStatus.DRAFT,
        db_index=True,
        help_text=_("Current workflow status of this mark entry."),
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_internal_marks",
        verbose_name=_("reviewed by"),
        help_text=_("Principal or administrator who approved or rejected these marks."),
    )
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)
    review_comment = models.TextField(
        _("review / rejection comment"),
        blank=True,
        help_text=_("Feedback provided by the reviewer (mandatory when rejecting marks to guide revisions)."),
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)

    class Meta:
        verbose_name = _("Internal Assessment Mark")
        verbose_name_plural = _("Internal Assessment Marks")
        ordering = ["-entered_at"]
        unique_together = ("student", "program", "subject")

    def __str__(self) -> str:
        student_name = self.student.get_full_name() or self.student.username
        return f"{student_name} - {self.subject} ({self.marks_obtained}/{self.max_marks}) [{self.get_status_display()}]"

    def clean(self):
        super().clean()
        if self.marks_obtained is not None and self.max_marks is not None:
            if self.marks_obtained > self.max_marks:
                raise ValidationError(
                    {
                        "marks_obtained": _(
                            f"Marks obtained ({self.marks_obtained}) cannot exceed maximum allowable marks ({self.max_marks})."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def percentage(self) -> float:
        """Calculate the percentage score achieved."""
        if self.max_marks > 0 and self.marks_obtained is not None:
            return round((self.marks_obtained / self.max_marks) * 100, 1)
        return 0.0

    @property
    def is_editable_by_faculty(self) -> bool:
        """Faculty can only edit or delete records in draft or rejected status."""
        return self.status in [MarkStatus.DRAFT, MarkStatus.REJECTED]

    @property
    def is_draft(self) -> bool:
        return self.status == MarkStatus.DRAFT

    @property
    def is_submitted(self) -> bool:
        return self.status == MarkStatus.SUBMITTED

    @property
    def is_approved(self) -> bool:
        return self.status == MarkStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == MarkStatus.REJECTED

    @property
    def is_published(self) -> bool:
        return self.status == MarkStatus.PUBLISHED
