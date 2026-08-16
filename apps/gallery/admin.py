"""
apps/gallery/admin.py
=====================
Django admin configuration for GalleryImage.
Tailored for non-technical office staff with photo previews, friendly help texts,
and Pillow-based image validation.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_image_file
from .models import GalleryImage


class GalleryImageAdminForm(forms.ModelForm):
    """Admin form for GalleryImage with friendly help text and validation."""

    class Meta:
        model = GalleryImage
        fields = "__all__"
        help_texts = {
            "image": _("Upload a photo of campus events, sports, or student life — landscape orientation works best, under 5MB."),
            "caption": _("Short description or title for this photo (e.g. 'Annual Sports Meet — 100m Sprint')."),
            "category": _("Optional album or group name to categorize this photo (e.g. 'Campus Life', 'Sports', 'Graduation')."),
            "display_order": _("Order in the photo album. Lower numbers (0, 1, 2...) appear first."),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "file"):
            validate_image_file(image)
        return image


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    """
    Admin configuration for managing the college photo gallery.
    """

    form = GalleryImageAdminForm
    list_display = ("thumbnail_preview", "caption_display", "category_badge", "display_order", "upload_date")
    list_display_links = ("thumbnail_preview", "caption_display")
    list_editable = ("display_order",)
    list_filter = ("category", "upload_date")
    search_fields = ("caption", "category")
    ordering = ("display_order", "-upload_date")
    readonly_fields = ("photo_preview", "upload_date")

    fieldsets = (
        (
            _("Photo Upload & Details"),
            {
                "fields": ("image", "photo_preview", "caption", "category"),
                "description": _("Select a high-resolution photo from your computer, give it a title, and assign it to an album."),
            },
        ),
        (
            _("Album Sequence & Info"),
            {
                "fields": ("display_order", "upload_date"),
                "description": _("Arrange photo order within the gallery and view the upload timestamp."),
            },
        ),
    )

    @admin.display(description=_("Photo"))
    def thumbnail_preview(self, obj: GalleryImage):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 70px; height: 50px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" />',
                obj.image.url,
                obj.caption or f"Gallery #{obj.id}",
            )
        return _("No photo")

    @admin.display(description=_("Caption / Title"), ordering="caption")
    def caption_display(self, obj: GalleryImage):
        return obj.caption if obj.caption else format_html('<span style="color: #94a3b8; font-style: italic;">Untitled (Photo #{})</span>', obj.id)

    @admin.display(description=_("Album / Category"), ordering="category")
    def category_badge(self, obj: GalleryImage):
        if obj.category:
            return format_html(
                '<span style="background-color: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 500;">📁 {}</span>',
                obj.category,
            )
        return format_html('<span style="color: #94a3b8;">General</span>')

    @admin.display(description=_("Current Photo Preview"))
    def photo_preview(self, obj: GalleryImage):
        if obj and obj.image:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="{}" style="max-width: 100%; max-height: 250px; object-fit: contain; border-radius: 6px; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.image.url,
                obj.caption or "Preview",
            )
        return _("Upload a photo above to see a preview.")
