"""
apps/gallery/migrations/0001_initial.py
=======================================
Initial migration for GalleryImage model.
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GalleryImage",
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
                    "image",
                    models.ImageField(
                        help_text="Upload a high-quality photograph of the campus, event, or facility.",
                        upload_to="gallery/images/",
                        verbose_name="image",
                    ),
                ),
                (
                    "caption",
                    models.CharField(
                        blank=True,
                        help_text="Short descriptive title or context for this photo.",
                        max_length=255,
                        verbose_name="caption / description",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        help_text="Optional grouping tag (e.g. 'Campus Infrastructure', 'Annual Day', 'Seminars', 'Sports').",
                        max_length=100,
                        verbose_name="category / album",
                    ),
                ),
                (
                    "upload_date",
                    models.DateTimeField(auto_now_add=True, verbose_name="upload date"),
                ),
                (
                    "display_order",
                    models.IntegerField(
                        default=0,
                        help_text="Order in gallery list (lower numbers appear first).",
                        verbose_name="display order",
                    ),
                ),
            ],
            options={
                "verbose_name": "Gallery Image",
                "verbose_name_plural": "Gallery Images",
                "ordering": ["display_order", "-upload_date"],
            },
        ),
    ]
