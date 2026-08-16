"""
apps/messaging/admin.py
=======================
Django admin configuration for Message model (Read-only audit log).
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Read-only audit log of in-app communications and broadcasts.
    """

    list_display = (
        "subject",
        "sender",
        "get_recipient_display",
        "sent_at",
        "is_read",
    )
    list_filter = ("broadcast_target_role", "is_read", "sent_at")
    search_fields = (
        "subject",
        "body",
        "sender__username",
        "sender__first_name",
        "sender__last_name",
        "recipient__username",
        "recipient__first_name",
        "recipient__last_name",
    )
    ordering = ("-sent_at",)
    readonly_fields = (
        "sender",
        "recipient",
        "broadcast_target_role",
        "subject",
        "body",
        "sent_at",
        "is_read",
    )

    fieldsets = (
        (
            _("Message Audit Record"),
            {
                "fields": (
                    "sender",
                    "recipient",
                    "broadcast_target_role",
                    "subject",
                    "body",
                    "sent_at",
                    "is_read",
                ),
            },
        ),
    )

    @admin.display(description=_("Recipient / Target"))
    def get_recipient_display(self, obj: Message) -> str:
        return obj.target_display

    def has_add_permission(self, request):
        """Staff must use the messaging portal UI to compose messages."""
        return False

    def has_change_permission(self, request, obj=None):
        """Audit records are immutable."""
        return False
