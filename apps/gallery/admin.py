"""
apps/gallery/admin.py
=====================
Django admin configuration for GalleryImage.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing the photo gallery.
    """

    list_display = ("id", "caption", "category", "display_order", "upload_date")
    list_editable = ("display_order",)
    list_filter = ("category",)
    search_fields = ("caption", "category")
    ordering = ("display_order", "-upload_date")

    fieldsets = (
        (
            _("Image & Description"),
            {
                "fields": ("image", "caption", "category"),
                "description": _("Upload photograph and assign an album or category name."),
            },
        ),
        (
            _("Ordering"),
            {
                "fields": ("display_order",),
                "description": _("Sequence order in the gallery (lower numbers appear first)."),
            },
        ),
    )
