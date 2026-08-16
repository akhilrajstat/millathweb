"""
apps/internal_marks/forms.py
============================
Forms for faculty mark entry, principal evaluation/review, and bulk publishing.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import User, UserRole
from apps.internal_marks.models import InternalMark, MarkStatus
from apps.programs.models import Program


class InternalMarkForm(forms.ModelForm):
    """
    Form for faculty to record or update internal marks for a student.
    """

    class Meta:
        model = InternalMark
        fields = ["student", "program", "subject", "max_marks", "marks_obtained"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-select"}),
            "program": forms.Select(attrs={"class": "form-select"}),
            "subject": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Pedagogy of Mathematics - Internal Test 1",
                }
            ),
            "max_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "20",
                }
            ),
            "marks_obtained": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Enter score awarded",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit student choices to approved students only, formatted with admission number
        students = (
            User.objects.filter(role=UserRole.STUDENT, is_approved=True)
            .select_related("student_profile")
            .order_by("first_name", "last_name", "username")
        )
        self.fields["student"].queryset = students
        self.fields["student"].label_from_instance = self._format_student_label
        self.fields["program"].queryset = Program.objects.filter(is_active=True).order_by("name")

    @staticmethod
    def _format_student_label(student: User) -> str:
        name = student.get_full_name() or student.username
        adm = ""
        if hasattr(student, "student_profile") and student.student_profile and student.student_profile.admission_number:
            adm = f" [Roll: {student.student_profile.admission_number}]"
        return f"{name}{adm} ({student.email})"

    def clean(self):
        cleaned_data = super().clean()
        max_marks = cleaned_data.get("max_marks")
        marks_obtained = cleaned_data.get("marks_obtained")

        if max_marks is not None and marks_obtained is not None:
            if marks_obtained > max_marks:
                self.add_error(
                    "marks_obtained",
                    ValidationError(
                        _(f"Marks obtained ({marks_obtained}) cannot exceed maximum marks ({max_marks})."),
                        code="marks_exceeded",
                    ),
                )

        student = cleaned_data.get("student")
        program = cleaned_data.get("program")
        subject = cleaned_data.get("subject")

        if student and program and subject:
            # Check duplicate unique_together on create
            existing = InternalMark.objects.filter(
                student=student,
                program=program,
                subject__iexact=subject.strip(),
            )
            if self.instance and self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)

            if existing.exists():
                raise ValidationError(
                    _(f"A mark entry already exists for student '{student.get_full_name() or student.username}' "
                      f"in subject '{subject}' for program '{program.name}'. "
                      f"Please edit the existing draft/rejected entry instead of creating a duplicate.")
                )

        return cleaned_data


class MarkReviewForm(forms.Form):
    """
    Form for Principal / Super Admin to approve or reject a submitted mark entry.
    """

    ACTION_APPROVE = "approve"
    ACTION_REJECT = "reject"

    ACTION_CHOICES = [
        (ACTION_APPROVE, _("Approve Marks")),
        (ACTION_REJECT, _("Reject & Request Revision")),
    ]

    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label=_("Review Decision"),
    )
    review_comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Required if rejecting: Provide specific instructions for faculty to correct...",
            }
        ),
        label=_("Review Comments / Revision Instructions"),
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get("action")
        comment = cleaned_data.get("review_comment", "").strip()

        if action == self.ACTION_REJECT and not comment:
            self.add_error(
                "review_comment",
                ValidationError(
                    _("A review comment is mandatory when rejecting marks to inform faculty what must be revised."),
                    code="rejection_comment_required",
                ),
            )
        return cleaned_data


class BulkPublishForm(forms.Form):
    """
    Form for Principal / Super Admin to publish all approved marks for an academic program.
    """

    program = forms.ModelChoiceField(
        queryset=Program.objects.filter(is_active=True).order_by("name"),
        required=False,
        empty_label=_("All Academic Programs (Global Bulk Publish)"),
        widget=forms.Select(attrs={"class": "form-select"}),
        label=_("Filter by Program"),
    )
