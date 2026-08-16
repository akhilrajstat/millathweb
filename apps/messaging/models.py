"""
apps/messaging/models.py
========================
Data model for individual and broadcast in-app messages within Millath College ERP.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole


class Message(models.Model):
    """
    In-app communication record.
    - If `recipient` is populated: direct message to that specific user.
    - If `recipient` is None: broadcast announcement sent by administrative staff.
      `broadcast_target_role` specifies either a specific target role (e.g. 'student')
      or empty string for all institutional users.
    """

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("sender"),
    )
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="received_messages",
        verbose_name=_("recipient"),
        help_text=_("Direct recipient user. Leave empty for administrative broadcast."),
    )
    broadcast_target_role = models.CharField(
        _("broadcast target role"),
        max_length=20,
        choices=UserRole.choices,
        blank=True,
        help_text=_(
            "Used only for broadcast announcements (recipient is None). "
            "Leave blank to broadcast to all roles."
        ),
    )
    subject = models.CharField(
        _("subject"),
        max_length=255,
        help_text=_("Brief subject or summary of the message."),
    )
    body = models.TextField(
        _("message body"),
        help_text=_("Plain-text message content."),
    )
    sent_at = models.DateTimeField(
        _("sent at"),
        auto_now_add=True,
        db_index=True,
    )
    is_read = models.BooleanField(
        _("is read"),
        default=False,
        help_text=_("Tracks whether the direct recipient has opened the message."),
    )

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="msg_recipient_read_idx"),
            models.Index(fields=["sent_at"], name="msg_sent_at_idx"),
        ]

    def __str__(self) -> str:
        if self.is_broadcast:
            target = self.get_broadcast_target_role_display() if self.broadcast_target_role else "All Users"
            return f"[Broadcast to {target}] {self.subject} (from {self.sender})"
        return f"[Direct to {self.recipient}] {self.subject} (from {self.sender})"

    @property
    def is_broadcast(self) -> bool:
        return self.recipient is None

    @property
    def target_display(self) -> str:
        if self.is_broadcast:
            if self.broadcast_target_role:
                return f"Broadcast: {self.get_broadcast_target_role_display()}"
            return "Broadcast: Everyone"
        return self.recipient.get_full_name() or self.recipient.username
