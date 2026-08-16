"""
apps/faculty/migrations/0001_initial.py
=======================================
Initial migration for FacultyProfile model.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FacultyProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "designation",
                    models.CharField(
                        help_text="Academic rank (e.g. 'Principal', 'Professor & HOD', 'Assistant Professor in Education').",
                        max_length=150,
                        verbose_name="designation",
                    ),
                ),
                (
                    "qualification",
                    models.CharField(
                        help_text="Degrees and certifications (e.g. 'M.Ed., Ph.D., UGC-NET').",
                        max_length=255,
                        verbose_name="qualifications",
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True,
                        help_text="Professional portrait photograph (square aspect ratio recommended).",
                        null=True,
                        upload_to="faculty/photos/",
                        verbose_name="profile photo",
                    ),
                ),
                (
                    "bio",
                    django_ckeditor_5.fields.CKEditor5Field(
                        blank=True,
                        help_text="Detailed academic background, publications, research interests, and awards.",
                        verbose_name="biography",
                    ),
                ),
                (
                    "specialization",
                    models.CharField(
                        blank=True,
                        help_text="Specific subject or pedagogy area (e.g. 'Educational Technology, Science Pedagogy').",
                        max_length=255,
                        verbose_name="area of specialization",
                    ),
                ),
                (
                    "email_display",
                    models.EmailField(
                        blank=True,
                        help_text="Publicly displayed contact email (can differ from login username/email).",
                        max_length=254,
                        verbose_name="display email",
                    ),
                ),
                (
                    "is_published",
                    models.BooleanField(
                        default=False,
                        help_text="Toggle public visibility. Staff can keep draft profiles unpublished until approved.",
                        verbose_name="is published",
                    ),
                ),
                (
                    "display_order",
                    models.IntegerField(
                        default=0,
                        help_text="Order in which this faculty member appears on the faculty page (lower numbers first).",
                        verbose_name="display order",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="Select the user account with faculty role to link.",
                        limit_choices_to={"role": "faculty"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faculty_profile",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user account",
                    ),
                ),
            ],
            options={
                "verbose_name": "Faculty Profile",
                "verbose_name_plural": "Faculty Profiles",
                "ordering": ["display_order", "user__first_name", "user__last_name"],
            },
        ),
    ]
