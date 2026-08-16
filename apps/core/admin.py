"""
apps/core/admin.py
==================
Django admin configuration for SiteSettings (singleton) and HomePageBanner.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSettings, HomePageBanner


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """
    Admin configuration for the global SiteSettings singleton.
    Organised with clear, friendly fieldsets for office staff.
    """

    fieldsets = (
        (
            _("Institution Identity"),
            {
                "fields": ("college_name", "tagline", "logo"),
                "description": _("General institutional branding details shown across headers and titles."),
            },
        ),
        (
            _("Contact Information"),
            {
                "fields": ("address", "phone_primary", "phone_secondary", "email_primary"),
                "description": _("Official contact numbers, address, and email displayed in the header and footer."),
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
                "description": _("Links to the college's official social media profiles."),
            },
        ),
        (
            _("Footer & Legal"),
            {
                "fields": ("footer_text",),
                "description": _("Copyright notice and affiliation / accreditation text."),
            },
        ),
    )

    def has_add_permission(self, request):
        # Prevent adding more than one singleton instance
        if SiteSettings.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Do not allow deletion of site settings
        return False


@admin.register(HomePageBanner)
class HomePageBannerAdmin(admin.ModelAdmin):
    """
    Admin configuration for hero banners with drag/order support and preview info.
    """

    list_display = ("title", "subtitle", "button_text", "display_order", "is_active")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "button_text")
    ordering = ("display_order", "-id")

    fieldsets = (
        (
            _("Banner Content"),
            {
                "fields": ("title", "subtitle", "image"),
                "description": _("Upload a crisp banner image and provide welcoming headline text."),
            },
        ),
        (
            _("Call to Action Button"),
            {
                "fields": ("button_text", "button_url"),
                "description": _("Optional button link displayed over the banner (e.g. 'Apply Now', '/programs/')."),
            },
        ),
        (
            _("Publishing & Display Settings"),
            {
                "fields": ("display_order", "is_active"),
                "description": _("Control ordering and toggle visibility without deleting."),
            },
        ),
    )
