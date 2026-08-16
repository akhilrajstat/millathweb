"""
apps/programs/migrations/0001_initial.py
========================================
Initial migration for Program model.
"""

from django.db import migrations, models
import django_ckeditor_5.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Program",
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
                    "name",
                    models.CharField(
                        help_text="Official course title (e.g. 'Bachelor of Education (B.Ed)').",
                        max_length=255,
                        verbose_name="program name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="URL-friendly identifier generated from the name.",
                        max_length=255,
                        unique=True,
                        verbose_name="slug",
                    ),
                ),
                (
                    "description",
                    django_ckeditor_5.fields.CKEditor5Field(
                        help_text="Comprehensive curriculum overview, objectives, and course outcomes.",
                        verbose_name="program description",
                    ),
                ),
                (
                    "duration",
                    models.CharField(
                        help_text="Program length (e.g. '2 Years (4 Semesters)').",
                        max_length=100,
                        verbose_name="duration",
                    ),
                ),
                (
                    "eligibility",
                    models.TextField(
                        help_text="Minimum qualifications, cutoff marks, or prerequisites required for admission.",
                        verbose_name="eligibility criteria",
                    ),
                ),
                (
                    "syllabus_pdf",
                    models.FileField(
                        blank=True,
                        help_text="Optional PDF download of the detailed curriculum / syllabus.",
                        null=True,
                        upload_to="programs/syllabus/",
                        verbose_name="syllabus document",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        help_text="Thumbnail/cover photo for the program card and banner.",
                        null=True,
                        upload_to="programs/images/",
                        verbose_name="featured image",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Toggle whether this course is publicly visible and accepting enquiries.",
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
                "verbose_name": "Academic Program",
                "verbose_name_plural": "Academic Programs",
                "ordering": ["name"],
            },
        ),
    ]
