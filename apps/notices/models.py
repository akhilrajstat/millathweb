"""
apps/notices/models.py
======================
Model for college announcements, circulars, exam schedules, and events.
"""

from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.validators import validate_file_size_5mb


class NoticeCategory(models.TextChoices):
    """
    Standard notice categories.
    """

    GENERAL = "general", _("General Notice")
    ACADEMIC = "academic", _("Academic Circular")
    EXAM = "exam", _("Examination")
    ADMISSION = "admission", _("Admission")
    EVENT = "event", _("College Event / Activity")


class Notice(models.Model):
    """
    Official notice or announcement.
    """

    title = models.CharField(
        _("notice title"),
        max_length=255,
        help_text=_("Clear, descriptive headline for this circular or announcement."),
    )
    slug = models.SlugField(
        _("slug"),
        max_length=255,
        unique=True,
        blank=True,
        help_text=_("URL slug automatically derived from the title."),
    )
    category = models.CharField(
        _("category"),
        max_length=20,
        choices=NoticeCategory.choices,
        default=NoticeCategory.GENERAL,
        db_index=True,
        help_text=_("Classification category for filtering and badges."),
    )
    description = CKEditor5Field(
        _("notice content"),
        config_name="extends",
        help_text=_("Full announcement text, details, and guidelines."),
    )
    file_attachment = models.FileField(
        _("file attachment"),
        upload_to="notices/attachments/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf"],
                message=_("Only PDF files are allowed for notice attachments."),
            ),
            validate_file_size_5mb,
        ],
        help_text=_("Optional PDF attachment for students/faculty to download (PDF only, max 5MB)."),
    )
    publish_date = models.DateField(
        _("publish date"),
        default=timezone.now,
        db_index=True,
        help_text=_("Official date shown on the circular."),
    )
    is_active = models.BooleanField(
        _("is active"),
        default=True,
        help_text=_("Toggle visibility on the public site."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Notice & Announcement")
        verbose_name_plural = _("Notices & Announcements")
        ordering = ["-publish_date", "-id"]

    def __str__(self) -> str:
        return f"[{self.get_category_display()}] {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Notice.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("notices:detail", kwargs={"slug": self.slug})
