"""
apps/gallery/models.py
======================
Model for campus photo gallery, event photos, and academic life moments.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class GalleryImage(models.Model):
    """
    Photograph stored in the college gallery with caption and optional category.
    """

    image = models.ImageField(
        _("image"),
        upload_to="gallery/images/",
        help_text=_("Upload a high-quality photograph of the campus, event, or facility."),
    )
    caption = models.CharField(
        _("caption / description"),
        max_length=255,
        blank=True,
        help_text=_("Short descriptive title or context for this photo."),
    )
    category = models.CharField(
        _("category / album"),
        max_length=100,
        blank=True,
        help_text=_("Optional grouping tag (e.g. 'Campus Infrastructure', 'Annual Day', 'Seminars', 'Sports')."),
    )
    upload_date = models.DateTimeField(
        _("upload date"),
        auto_now_add=True,
    )
    display_order = models.IntegerField(
        _("display order"),
        default=0,
        help_text=_("Order in gallery list (lower numbers appear first)."),
    )

    class Meta:
        verbose_name = _("Gallery Image")
        verbose_name_plural = _("Gallery Images")
        ordering = ["display_order", "-upload_date"]

    def __str__(self) -> str:
        return self.caption or f"Gallery Image #{self.id}"
