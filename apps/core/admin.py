"""
apps/core/admin.py
==================
Django admin configuration for SiteSettings (singleton) and HomePageBanner.
Tailored for non-technical office staff with thumbnail previews, friendly help text,
and robust image validation.
"""

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import HomePageBanner, SiteSettings
from .validators import validate_image_file

# ---------------------------------------------------------------------------
# Global Admin Branding
# ---------------------------------------------------------------------------
admin.site.site_header = "Millath College — Website Management"
admin.site.site_title = "Millath College Admin"
admin.site.index_title = "Website Management Portal"


# ---------------------------------------------------------------------------
# SiteSettings Admin
# ---------------------------------------------------------------------------
class SiteSettingsAdminForm(forms.ModelForm):
    """Admin form for SiteSettings with friendly guidance and file validation."""

    class Meta:
        model = SiteSettings
        fields = "__all__"
        help_texts = {
            "college_name": _("Official institution name displayed across the website header and document titles."),
            "tagline": _("Short motto or tagline displayed below the college name (e.g. 'Shaping Future Educators')."),
            "logo": _("Upload college emblem or logo (PNG with transparent background or high-res JPG, under 5MB)."),
            "address": _("Complete postal address of the campus displayed in the website footer and contact page."),
            "phone_primary": _("Main office phone number for general enquiries (e.g. +91 483 1234567)."),
            "phone_secondary": _("Alternate contact number or admissions helpdesk line."),
            "email_primary": _("Primary official email address for public enquiries (e.g. millathcollege669@yahoo.com)."),
            "website_url": _("Official website web address (e.g. https://millathcollege.org)."),
            "facebook_url": _("Full link to the official Facebook page (leave blank if none)."),
            "twitter_url": _("Full link to the official Twitter / X profile (leave blank if none)."),
            "instagram_url": _("Full link to the official Instagram profile (leave blank if none)."),
            "youtube_url": _("Full link to the official YouTube channel (leave blank if none)."),
            "linkedin_url": _("Full link to the official LinkedIn page (leave blank if none)."),
            "footer_text": _("Copyright and affiliation text shown at the very bottom of every webpage."),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        if logo and hasattr(logo, "file"):
            validate_image_file(logo)
        return logo


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the global SiteSettings singleton.
    Organised with clear, friendly fieldsets for office staff.
    """

    form = SiteSettingsAdminForm
    readonly_fields = ("logo_preview",)

    fieldsets = (
        (
            _("Institution Identity & Branding"),
            {
                "fields": ("college_name", "tagline", "logo", "logo_preview"),
                "description": _("General institutional branding details shown across website headers and banners."),
            },
        ),
        (
            _("Campus Contact Information"),
            {
                "fields": ("address", "phone_primary", "phone_secondary", "email_primary", "website_url"),
                "description": _("Official contact numbers, address, and email displayed in the header, footer, and contact page."),
            },
        ),
        (
            _("Social Media Links"),
            {
                "fields": (
                    "facebook_url",
                    "twitter_url",
                    "instagram_url",
                    "youtube_url",
                    "linkedin_url",
                ),
                "classes": ("collapse",),
                "description": _("Links to the college's official social media profiles. Leave blank if not available."),
            },
        ),
        (
            _("Footer & Legal Notice"),
            {
                "fields": ("footer_text",),
                "description": _("Copyright notice and affiliation / accreditation text shown at the bottom of every page."),
            },
        ),
    )

    @admin.display(description=_("Current Logo Preview"))
    def logo_preview(self, obj: SiteSettings):
        if obj and obj.logo:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="College Logo" style="max-height: 80px; max-width: 250px; object-fit: contain; border-radius: 6px; padding: 4px; background: #f8fafc; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.logo.url,
            )
        return _("No logo uploaded yet.")

    def has_add_permission(self, request):
        # Prevent adding more than one singleton instance
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Do not allow deletion of site settings
        return False


# ---------------------------------------------------------------------------
# HomePageBanner Admin
# ---------------------------------------------------------------------------
class HomePageBannerAdminForm(forms.ModelForm):
    """Admin form for HomePageBanner with friendly guidance and file validation."""

    class Meta:
        model = HomePageBanner
        fields = "__all__"
        help_texts = {
            "title": _("Main headline text displayed prominently on the slide (e.g. 'Welcome to Millath College of Education')."),
            "subtitle": _("Optional secondary descriptive sentence displayed below the main headline."),
            "image": _("Upload a high-resolution hero photo — landscape orientation (around 1920x800 px) works best, under 5MB."),
            "button_text": _("Optional call-to-action button text (e.g. 'Explore Academic Programs' or 'Apply Now')."),
            "button_url": _("Where the button takes visitors (e.g. '/programs/' or an external link)."),
            "display_order": _("Sequence order in the homepage carousel. Lower numbers (0, 1, 2...) appear first."),
            "is_active": _("Check this box to show this banner on the homepage. Uncheck to temporarily hide it without deleting."),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and hasattr(image, "file"):
            validate_image_file(image)
        return image


@admin.register(HomePageBanner)
class HomePageBannerAdmin(admin.ModelAdmin):
    """
    Admin configuration for hero banners with photo preview and friendly controls.
    """

    form = HomePageBannerAdminForm
    list_display = ("thumbnail_preview", "title", "subtitle", "button_text", "display_order", "is_active")
    list_display_links = ("thumbnail_preview", "title")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "button_text")
    ordering = ("display_order", "-id")
    readonly_fields = ("banner_preview",)

    fieldsets = (
        (
            _("Banner Photo & Content"),
            {
                "fields": ("title", "subtitle", "image", "banner_preview"),
                "description": _("Upload a high-quality banner photo and enter welcoming headline text for visitors."),
            },
        ),
        (
            _("Call to Action Button (Optional)"),
            {
                "fields": ("button_text", "button_url"),
                "description": _("Add a clickable button over the banner slide to direct visitors to programs, admissions, or notices."),
            },
        ),
        (
            _("Display Order & Visibility"),
            {
                "fields": ("display_order", "is_active"),
                "description": _("Control slide ordering (lower numbers first) and toggle whether this banner is currently visible on the live site."),
            },
        ),
    )

    @admin.display(description=_("Slide Preview"))
    def thumbnail_preview(self, obj: HomePageBanner):
        if obj and obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="width: 80px; height: 45px; object-fit: cover; border-radius: 4px; border: 1px solid #cbd5e1; box-shadow: 0 1px 2px rgba(0,0,0,0.05);" />',
                obj.image.url,
                obj.title,
            )
        return _("No image")

    @admin.display(description=_("Current Banner Preview"))
    def banner_preview(self, obj: HomePageBanner):
        if obj and obj.image:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="{}" style="max-width: 100%; max-height: 220px; object-fit: cover; border-radius: 6px; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.image.url,
                obj.title,
            )
        return _("Upload an image above to see a preview.")
