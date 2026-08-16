"""
apps/faculty/models.py
======================
Public-facing faculty member profiles.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class FacultyProfile(models.Model):
    """
    Public faculty biography and teaching profile linked to a faculty User account.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="faculty_profile",
        limit_choices_to={"role": "faculty"},
        verbose_name=_("user account"),
        help_text=_("Select the user account with faculty role to link."),
    )
    designation = models.CharField(
        _("designation"),
        max_length=150,
        help_text=_("Academic rank (e.g. 'Principal', 'Professor & HOD', 'Assistant Professor in Education')."),
    )
    qualification = models.CharField(
        _("qualifications"),
        max_length=255,
        help_text=_("Degrees and certifications (e.g. 'M.Ed., Ph.D., UGC-NET')."),
    )
    photo = models.ImageField(
        _("profile photo"),
        upload_to="faculty/photos/",
        blank=True,
        null=True,
        help_text=_("Professional portrait photograph (square aspect ratio recommended)."),
    )
    bio = CKEditor5Field(
        _("biography"),
        config_name="extends",
        blank=True,
        help_text=_("Detailed academic background, publications, research interests, and awards."),
    )
    specialization = models.CharField(
        _("area of specialization"),
        max_length=255,
        blank=True,
        help_text=_("Specific subject or pedagogy area (e.g. 'Educational Technology, Science Pedagogy')."),
    )
    email_display = models.EmailField(
        _("display email"),
        blank=True,
        help_text=_("Publicly displayed contact email (can differ from login username/email)."),
    )
    is_published = models.BooleanField(
        _("is published"),
        default=False,
        help_text=_("Toggle public visibility. Staff can keep draft profiles unpublished until approved."),
    )
    display_order = models.IntegerField(
        _("display order"),
        default=0,
        help_text=_("Order in which this faculty member appears on the faculty page (lower numbers first)."),
    )

    class Meta:
        verbose_name = _("Faculty Profile")
        verbose_name_plural = _("Faculty Profiles")
        ordering = ["display_order", "user__first_name", "user__last_name"]

    def __str__(self) -> str:
        name = self.user.get_full_name() or self.user.username
        return f"{name} — {self.designation}"

    def get_absolute_url(self) -> str:
        return reverse("faculty:detail", kwargs={"pk": self.pk})

    @property
    def full_name(self) -> str:
        return self.user.get_full_name() or self.user.username

    @property
    def contact_email(self) -> str:
        return self.email_display or self.user.email
