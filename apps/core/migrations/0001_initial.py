"""
apps/core/migrations/0001_initial.py
====================================
Initial migration for core models (SiteSettings and HomePageBanner).
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
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
                    "college_name",
                    models.CharField(
                        default="Millath College of Education",
                        help_text="The official name of the institution.",
                        max_length=255,
                        verbose_name="college name",
                    ),
                ),
                (
                    "tagline",
                    models.CharField(
                        blank=True,
                        default="Shaping Future Educators with Excellence & Values",
                        help_text="Catchphrase or motto shown in the header/footer.",
                        max_length=255,
                        verbose_name="tagline",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        help_text="College logo image (transparent PNG recommended).",
                        null=True,
                        upload_to="core/logos/",
                        verbose_name="logo",
                    ),
                ),
                (
                    "address",
                    models.TextField(
                        blank=True,
                        default="Millath College Campus, Education Enclave, Kerala, India",
                        help_text="Full physical postal address of the college.",
                        verbose_name="address",
                    ),
                ),
                (
                    "phone_primary",
                    models.CharField(
                        blank=True,
                        default="+91 483 1234567",
                        help_text="Main office contact number.",
                        max_length=20,
                        verbose_name="primary phone",
                    ),
                ),
                (
                    "phone_secondary",
                    models.CharField(
                        blank=True,
                        help_text="Alternative contact number or admission desk.",
                        max_length=20,
                        verbose_name="secondary phone",
                    ),
                ),
                (
                    "email_primary",
                    models.EmailField(
                        blank=True,
                        default="info@millathcollege.edu.in",
                        help_text="Main contact email for public enquiries.",
                        max_length=254,
                        verbose_name="primary email",
                    ),
                ),
                ("facebook_url", models.URLField(blank=True, verbose_name="Facebook URL")),
                ("twitter_url", models.URLField(blank=True, verbose_name="Twitter / X URL")),
                ("instagram_url", models.URLField(blank=True, verbose_name="Instagram URL")),
                ("youtube_url", models.URLField(blank=True, verbose_name="YouTube URL")),
                ("linkedin_url", models.URLField(blank=True, verbose_name="LinkedIn URL")),
                (
                    "footer_text",
                    models.TextField(
                        blank=True,
                        default="© Millath College. All Rights Reserved. Affiliated to University / NCTE Approved.",
                        help_text="Text displayed at the bottom of every page.",
                        verbose_name="footer text",
                    ),
                ),
            ],
            options={
                "verbose_name": "Site Settings",
                "verbose_name_plural": "Site Settings",
            },
        ),
        migrations.CreateModel(
            name="HomePageBanner",
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
                        help_text="Main heading on the hero banner slide.",
                        max_length=255,
                        verbose_name="banner title",
                    ),
                ),
                (
                    "subtitle",
                    models.CharField(
                        blank=True,
                        help_text="Secondary description or tagline for the slide.",
                        max_length=255,
                        verbose_name="subtitle",
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="High-resolution hero background image (1920x800 recommended).",
                        upload_to="core/banners/",
                        verbose_name="banner image",
                    ),
                ),
                (
                    "button_text",
                    models.CharField(
                        blank=True,
                        help_text="Optional CTA button text (e.g. 'Explore Programs').",
                        max_length=50,
                        verbose_name="button text",
                    ),
                ),
                (
                    "button_url",
                    models.CharField(
                        blank=True,
                        help_text="Target URL or path for the CTA button (e.g. '/programs/').",
                        max_length=255,
                        verbose_name="button URL",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Uncheck to hide this banner slide from the homepage.",
                        verbose_name="active",
                    ),
                ),
                (
                    "display_order",
                    models.IntegerField(
                        default=0,
                        help_text="Lower numbers appear first in the carousel.",
                        verbose_name="display order",
                    ),
                ),
            ],
            options={
                "verbose_name": "Home Page Banner",
                "verbose_name_plural": "Home Page Banners",
                "ordering": ["display_order", "-id"],
            },
        ),
    ]
