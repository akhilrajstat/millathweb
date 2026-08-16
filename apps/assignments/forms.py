"""
apps/assignments/forms.py
=========================
Form definitions for assignments creation, student submission, and faculty grading.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget

from apps.assignments.models import Assignment, Submission


class AssignmentForm(forms.ModelForm):
    """
    Form for faculty to create and update assignments.
    """

    class Meta:
        model = Assignment
        fields = [
            "title",
            "program",
            "due_date",
            "max_marks",
            "attachment",
            "description",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., Pedagogy of Physical Science - Unit 1 Assignment",
                }
            ),
            "program": forms.Select(attrs={"class": "form-select"}),
            "due_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "max_marks": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1,
                    "placeholder": "100",
                }
            ),
            "attachment": forms.FileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Format due_date for HTML5 datetime-local input if editing existing instance
        if self.instance and self.instance.pk and self.instance.due_date:
            self.initial["due_date"] = self.instance.due_date.strftime("%Y-%m-%dT%H:%M")
        self.fields["program"].empty_label = "All Academic Programs (Global Assignment)"

    def clean_due_date(self):
        due_date = self.cleaned_data.get("due_date")
        if due_date and due_date < timezone.now() and not self.instance.pk:
            raise ValidationError(
                _("The assignment due date cannot be in the past when creating a new assignment."),
                code="past_due_date",
            )
        return due_date


class SubmissionForm(forms.ModelForm):
    """
    Form for students to upload or resubmit their assignment file.
    """

    class Meta:
        model = Submission
        fields = ["submitted_file"]
        widgets = {
            "submitted_file": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png",
                }
            ),
        }
        help_texts = {
            "submitted_file": _("Supported formats: PDF, DOC, DOCX, JPG, JPEG, PNG (Max 5MB)."),
        }


class GradeSubmissionForm(forms.ModelForm):
    """
    Form for faculty instructors to evaluate and grade student submissions.
    """

    class Meta:
        model = Submission
        fields = ["marks_obtained", "feedback"]
        widgets = {
            "marks_obtained": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "placeholder": "Enter marks awarded",
                }
            ),
            "feedback": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Provide qualitative feedback, corrections, or constructive remarks for the student...",
                }
            ),
        }

    def __init__(self, *args, assignment_max_marks=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment_max_marks = assignment_max_marks
        if self.assignment_max_marks:
            self.fields["marks_obtained"].widget.attrs["max"] = self.assignment_max_marks
            self.fields["marks_obtained"].help_text = _(
                f"Maximum achievable marks for this assignment: {self.assignment_max_marks}"
            )

    def clean_marks_obtained(self):
        marks = self.cleaned_data.get("marks_obtained")
        if marks is not None:
            if marks < 0:
                raise ValidationError(_("Marks obtained cannot be negative."))
            if self.assignment_max_marks is not None and marks > self.assignment_max_marks:
                raise ValidationError(
                    _(f"Marks obtained ({marks}) cannot exceed maximum allowable marks ({self.assignment_max_marks}).")
                )
        return marks
