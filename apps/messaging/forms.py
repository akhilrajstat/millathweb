"""
apps/messaging/forms.py
=======================
Forms for composing direct messages and administrative broadcast announcements.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import UserRole
from apps.messaging.models import Message

User = get_user_model()


class ComposeMessageForm(forms.ModelForm):
    """
    Message composition form.
    Dynamically adjusts fields based on whether the sender has broadcast privileges
    (Super Admin or Office Staff).
    """

    MESSAGE_TYPE_CHOICES = [
        ("direct", _("Direct Message to Individual User")),
        ("broadcast", _("Broadcast Announcement (All / Role)")),
    ]

    BROADCAST_ROLE_CHOICES = [
        ("", _("All Institutional Users (Everyone)")),
        (UserRole.STUDENT.value, _("All Students")),
        (UserRole.FACULTY.value, _("All Faculty Members")),
        (UserRole.OFFICE_STAFF.value, _("All Office Staff")),
        (UserRole.SUPER_ADMIN.value, _("All Administrators")),
    ]

    message_type = forms.ChoiceField(
        choices=MESSAGE_TYPE_CHOICES,
        initial="direct",
        required=False,
        label=_("Message Type"),
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
    )

    recipient = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label=_("Recipient User"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_recipient_select"}),
        help_text=_("Select the approved user to send a direct message to."),
    )

    broadcast_role = forms.ChoiceField(
        choices=BROADCAST_ROLE_CHOICES,
        required=False,
        label=_("Broadcast Target Audience"),
        widget=forms.Select(attrs={"class": "form-select", "id": "id_broadcast_select"}),
    )

    class Meta:
        model = Message
        fields = ["subject", "body"]
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter subject line"}),
            "body": forms.Textarea(attrs={"class": "form-control", "rows": 6, "placeholder": "Type your message here..."}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # Filter recipients to approved active users excluding the sender
        if user:
            self.fields["recipient"].queryset = (
                User.objects.filter(is_approved=True, is_active=True)
                .exclude(pk=user.pk)
                .order_by("role", "first_name", "last_name")
            )
            # Custom label formatting for recipient dropdown
            self.fields["recipient"].label_from_instance = (
                lambda u: f"{u.get_full_name() or u.username} ({u.get_role_display()}) — {u.email}"
            )

        # Check if user has broadcast permission
        self.can_broadcast = False
        if user:
            self.can_broadcast = (
                user.is_superuser
                or user.is_staff
                or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]
            )

        if not self.can_broadcast:
            # Hide broadcast options for regular students/faculty
            self.fields["message_type"].widget = forms.HiddenInput()
            self.fields["broadcast_role"].widget = forms.HiddenInput()
            self.fields["recipient"].required = True

    def clean(self):
        cleaned_data = super().clean()
        msg_type = cleaned_data.get("message_type", "direct")
        recipient = cleaned_data.get("recipient")
        broadcast_role = cleaned_data.get("broadcast_role", "")

        if msg_type == "broadcast":
            if not self.can_broadcast:
                raise ValidationError(
                    _("You do not have permission to send broadcast messages.")
                )
            cleaned_data["recipient"] = None
            cleaned_data["broadcast_target_role"] = broadcast_role
        else:
            if not recipient:
                self.add_error("recipient", _("Please select a recipient for your direct message."))
            cleaned_data["broadcast_target_role"] = ""

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.sender = self.user
        instance.recipient = self.cleaned_data.get("recipient")
        instance.broadcast_target_role = self.cleaned_data.get("broadcast_target_role", "")
        if commit:
            instance.save()
        return instance
