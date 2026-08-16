"""
apps/messaging/views.py
=======================
Views for internal direct messaging, administrative broadcasts, and inbox management.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, ListView

from apps.accounts.models import UserRole
from apps.messaging.forms import ComposeMessageForm
from apps.messaging.models import Message


class InboxView(LoginRequiredMixin, ListView):
    """
    Displays direct messages addressed to the current user as well as
    broadcast announcements targeting the user's role or the entire institution.
    """

    model = Message
    template_name = "messaging/inbox.html"
    context_object_name = "messages_list"
    paginate_by = 20
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        user = self.request.user
        # Direct messages to user OR broadcast messages matching user role or global ("")
        return (
            Message.objects.filter(
                Q(recipient=user)
                | Q(recipient__isnull=True, broadcast_target_role=user.role)
                | Q(recipient__isnull=True, broadcast_target_role="")
            )
            .select_related("sender", "recipient")
            .order_by("-sent_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "inbox"
        return context


class SentView(LoginRequiredMixin, ListView):
    """
    Displays all direct and broadcast messages composed and sent by the current user.
    """

    model = Message
    template_name = "messaging/sent.html"
    context_object_name = "messages_list"
    paginate_by = 20
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        return (
            Message.objects.filter(sender=self.request.user)
            .select_related("sender", "recipient")
            .order_by("-sent_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "sent"
        return context


class ComposeView(LoginRequiredMixin, FormView):
    """
    Compose and send a direct message or institutional broadcast announcement.
    Enforces strict role permissions: students and faculty attempting broadcast
    POSTs are rejected with HTTP 403.
    """

    template_name = "messaging/compose.html"
    form_class = ComposeMessageForm
    success_url = reverse_lazy("messaging:sent")
    login_url = reverse_lazy("accounts:login")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = request.user
        can_broadcast = (
            user.is_superuser
            or user.is_staff
            or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]
        )
        msg_type = request.POST.get("message_type", "direct")

        # Security check: Unauthorized broadcast attempt rejected with 403 Forbidden
        if msg_type == "broadcast" and not can_broadcast:
            return HttpResponseForbidden(
                "403 Forbidden: You do not have permission to send broadcast messages."
            )

        return super().post(request, *args, **kwargs)

    def form_valid(self, form: ComposeMessageForm) -> HttpResponse:
        msg = form.save()
        if msg.is_broadcast:
            messages.success(
                self.request,
                _("Broadcast announcement published successfully to targeted audience."),
            )
        else:
            messages.success(
                self.request,
                _(f"Direct message sent successfully to {msg.recipient.get_full_name() or msg.recipient.username}."),
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "compose"
        context["can_broadcast"] = (
            self.request.user.is_superuser
            or self.request.user.is_staff
            or self.request.user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]
        )
        return context


class MessageDetailView(LoginRequiredMixin, DetailView):
    """
    Displays full message content.
    Automatically marks direct messages as read when viewed by the intended recipient.
    Strictly scoped to messages where the user is sender, direct recipient, or broadcast recipient.
    """

    model = Message
    template_name = "messaging/detail.html"
    context_object_name = "message_item"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        user = self.request.user
        # Strict isolation: Only allow access to messages where user is sender, direct recipient,
        # or targeted by broadcast
        return Message.objects.filter(
            Q(recipient=user)
            | Q(sender=user)
            | Q(recipient__isnull=True, broadcast_target_role=user.role)
            | Q(recipient__isnull=True, broadcast_target_role="")
        ).select_related("sender", "recipient")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Mark as read if user is the direct recipient
        if obj.recipient == self.request.user and not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=["is_read"])
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "detail"
        return context
