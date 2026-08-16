"""
apps/notices/migrations/0001_initial.py
=======================================
Initial migration for Notice model.
"""

from django.db import migrations, models
import django.utils.timezone
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Notice",
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
                    "title",
                    models.CharField(
                        help_text="Clear, descriptive headline for this circular or announcement.",
                        max_length=255,
                        verbose_name="notice title",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="URL slug automatically derived from the title.",
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("general", "General Notice"),
                            ("academic", "Academic Circular"),
                            ("exam", "Examination"),
                            ("admission", "Admission"),
                            ("event", "College Event / Activity"),
                        ],
                        db_index=True,
                        default="general",
                        help_text="Classification category for filtering and badges.",
                        max_length=20,
                        verbose_name="category",
                    ),
                ),
                (
                    "description",
                    django_ckeditor_5.fields.CKEditor5Field(
                        help_text="Full announcement text, details, and guidelines.",
                        verbose_name="notice content",
                    ),
                ),
                (
                    "file_attachment",
                    models.FileField(
                        blank=True,
                        help_text="Optional PDF or document attachment for students/faculty to download.",
                        null=True,
                        upload_to="notices/attachments/",
                        verbose_name="file attachment",
                    ),
                ),
                (
                    "publish_date",
                    models.DateField(
                        db_index=True,
                        default=django.utils.timezone.now,
                        help_text="Official date shown on the circular.",
                        verbose_name="publish date",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Toggle visibility on the public site.",
                        verbose_name="is active",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
            ],
            options={
                "verbose_name": "Notice & Announcement",
                "verbose_name_plural": "Notices & Announcements",
                "ordering": ["-publish_date", "-id"],
            },
        ),
    ]
