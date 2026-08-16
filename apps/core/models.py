"""
apps/core/models.py
===================
Models for global site settings (singleton) and homepage hero banners.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """
    Singleton model for global college website settings, contact info,
    branding, and social links.
    """

    college_name = models.CharField(
        _("college name"),
        max_length=255,
        default="Millath College of Education",
        help_text=_("The official name of the institution."),
    )
    tagline = models.CharField(
        _("tagline"),
        max_length=255,
        blank=True,
        default="Shaping Future Educators with Excellence & Values",
        help_text=_("Catchphrase or motto shown in the header/footer."),
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="core/logos/",
        blank=True,
        null=True,
        help_text=_("College logo image (transparent PNG recommended)."),
    )
    address = models.TextField(
        _("address"),
        blank=True,
        default="Millath College Campus, Education Enclave, Kerala, India",
        help_text=_("Full physical postal address of the college."),
    )
    phone_primary = models.CharField(
        _("primary phone"),
        max_length=20,
        blank=True,
        default="+91 483 1234567",
        help_text=_("Main office contact number."),
    )
    phone_secondary = models.CharField(
        _("secondary phone"),
        max_length=20,
        blank=True,
        help_text=_("Alternative contact number or admission desk."),
    )
    email_primary = models.EmailField(
        _("primary email"),
        blank=True,
        default="millathcollege669@yahoo.com",
        help_text=_("Main contact email for public enquiries."),
    )
    website_url = models.URLField(
        _("website URL"),
        blank=True,
        default="https://millathcollege.org",
        help_text=_("Official website address of the institution."),
    )

    # Social media URLs
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    twitter_url = models.URLField(_("Twitter / X URL"), blank=True)
    instagram_url = models.URLField(_("Instagram URL"), blank=True)
    youtube_url = models.URLField(_("YouTube URL"), blank=True)
    linkedin_url = models.URLField(_("LinkedIn URL"), blank=True)

    footer_text = models.TextField(
        _("footer text"),
        blank=True,
        default="© Millath College. All Rights Reserved. Affiliated to University / NCTE Approved.",
        help_text=_("Text displayed at the bottom of every page."),
    )

    class Meta:
        verbose_name = _("Site Settings")
        verbose_name_plural = _("Site Settings")

    @property
    def logo_url(self) -> str:
        """
        Return the uploaded custom logo URL if present and file exists on storage,
        otherwise fall back to the default static official college logo.
        """
        from django.templatetags.static import static
        if self.logo:
            try:
                if self.logo.storage.exists(self.logo.name):
                    return self.logo.url
            except Exception:
                pass
        return static("images/college_logo.png")

    def __str__(self) -> str:
        return self.college_name

    def save(self, *args, **kwargs):
        """
        Enforce singleton: always save as primary key 1.
        """
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Prevent deletion of singleton instance."""
        pass

    @classmethod
    def get_solo(cls):
        """
        Retrieve or create the single SiteSettings instance.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomePageBanner(models.Model):
    """
    Hero banner slides displayed on the homepage.
    """

    title = models.CharField(
        _("banner title"),
        max_length=255,
        help_text=_("Main heading on the hero banner slide."),
    )
    subtitle = models.CharField(
        _("subtitle"),
        max_length=255,
        blank=True,
        help_text=_("Secondary description or tagline for the slide."),
    )
    image = models.ImageField(
        _("banner image"),
        upload_to="core/banners/",
        help_text=_("High-resolution hero background image (1920x800 recommended)."),
    )
    button_text = models.CharField(
        _("button text"),
        max_length=50,
        blank=True,
        help_text=_("Optional CTA button text (e.g. 'Explore Programs')."),
    )
    button_url = models.CharField(
        _("button URL"),
        max_length=255,
        blank=True,
        help_text=_("Target URL or path for the CTA button (e.g. '/programs/')."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Uncheck to hide this banner slide from the homepage."),
    )
    display_order = models.IntegerField(
        _("display order"),
        default=0,
        help_text=_("Lower numbers appear first in the carousel."),
    )

    class Meta:
        verbose_name = _("Home Page Banner")
        verbose_name_plural = _("Home Page Banners")
        ordering = ["display_order", "-id"]

    def __str__(self) -> str:
        return self.title
