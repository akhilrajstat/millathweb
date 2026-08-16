"""
apps/programs/models.py
=======================
Model for academic courses and degree programs offered at Millath College.
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.validators import validate_file_size_5mb


class Program(models.Model):
    """
    Academic program (e.g., B.Ed, M.Ed, D.El.Ed).
    """

    name = models.CharField(
        _("program name"),
        max_length=255,
        help_text=_("Official course title (e.g. 'Bachelor of Education (B.Ed)')."),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("URL-friendly identifier generated from the name."),
    )
    description = CKEditor5Field(
        _("program description"),
        config_name="extends",
        help_text=_("Comprehensive curriculum overview, objectives, and course outcomes."),
    )
    duration = models.CharField(
        _("duration"),
        max_length=100,
        help_text=_("Program length (e.g. '2 Years (4 Semesters)')."),
    )
    eligibility = models.TextField(
        _("eligibility criteria"),
        help_text=_("Minimum qualifications, cutoff marks, or prerequisites required for admission."),
    )
    syllabus_pdf = models.FileField(
        _("syllabus document"),
        upload_to="programs/syllabus/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"],
                message=_("Only PDF files are allowed for syllabus documents."),
            ),
            validate_file_size_5mb,
        ],
        help_text=_("Optional PDF download of the detailed curriculum / syllabus (PDF only, max 5MB)."),
    )
    image = models.ImageField(
        _("featured image"),
        upload_to="programs/images/",
        blank=True,
        null=True,
        help_text=_("Thumbnail/cover photo for the program card and banner."),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Toggle whether this course is publicly visible and accepting enquiries."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Academic Program")
        verbose_name_plural = _("Academic Programs")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Program.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("programs:detail", kwargs={"slug": self.slug})
