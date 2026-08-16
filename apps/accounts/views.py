"""
apps/accounts/views.py
=======================
Authentication, Self-Registration, Dashboard, and Profile Management views.
"""

from typing import Optional
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.accounts.forms import (
    FacultySelfProfileForm,
    RegistrationForm,
    StudentSelfProfileForm,
)
from apps.accounts.models import StudentProfile, UserRole
from apps.faculty.models import FacultyProfile


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP address from request headers."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class CustomLoginView(LoginView):
    """
    Extends Django's LoginView to gate unapproved accounts.
    """

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()

        if not user.is_approved:
            form.add_error(
                None,
                _(
                    "Your account is pending approval by an administrator. "
                    "You will be notified once access is granted."
                ),
            )
            return self.form_invalid(form)

        return super().form_valid(form)


class RegisterView(FormView):
    """
    Public self-registration view for Students and Faculty members.
    Enforces IP-based rate limiting (max 3 registration attempts per hour).
    """

    template_name = "accounts/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("accounts:login")

    RATE_LIMIT_ATTEMPTS = 3
    RATE_LIMIT_TIMEOUT_SECONDS = 3600  # 1 hour

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        client_ip = get_client_ip(request)
        cache_key = f"reg_attempts_{client_ip}"
        attempts = cache.get(cache_key, 0)

        if attempts >= self.RATE_LIMIT_ATTEMPTS:
            messages.error(
                request,
                _(
                    "Too many registration requests from your network. "
                    "Please wait a while before trying again."
                ),
            )
            return render(
                request,
                self.template_name,
                {"form": self.get_form(), "rate_limited": True},
                status=429,
            )

        form = self.get_form()
        if form.is_valid():
            # Increment attempt counter on submission
            cache.set(cache_key, attempts + 1, timeout=self.RATE_LIMIT_TIMEOUT_SECONDS)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request,
            _(
                "Your registration request has been submitted successfully! "
                "Your account is currently pending administrator verification. "
                "You will receive an email once approved."
            ),
        )
        return render(
            self.request,
            "accounts/register_success.html",
            {"registered_user": user},
        )


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Authenticated ERP dashboard showing personal profile summary and quick links.
    """

    template_name = "accounts/dashboard.html"
    login_url = reverse_lazy("accounts:login")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["user_role_label"] = user.get_role_display()

        if user.role == UserRole.STUDENT:
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            context["student_profile"] = student_profile
        elif user.role == UserRole.FACULTY:
            faculty_profile, _ = FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "designation": "Faculty Member",
                    "qualification": "Pending Verification",
                },
            )
            context["faculty_profile"] = faculty_profile

        return context


class ProfileView(LoginRequiredMixin, View):
    """
    Self-service profile view allowing logged-in students or faculty
    to view and update their own profile information only.
    Enforces strict queryset scoping: users can NEVER query or edit another user's profile.
    """

    template_name = "accounts/profile.html"
    login_url = reverse_lazy("accounts:login")

    def get(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        context = {"user": user, "role": user.role}

        if user.role == UserRole.STUDENT:
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            context["student_profile"] = student_profile
            context["form"] = StudentSelfProfileForm(instance=student_profile)
        elif user.role == UserRole.FACULTY:
            faculty_profile, _ = FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "designation": "Faculty Member",
                    "qualification": "Pending Verification",
                },
            )
            context["faculty_profile"] = faculty_profile
            context["form"] = FacultySelfProfileForm(instance=faculty_profile)
        else:
            context["is_staff_user"] = True

        return render(request, self.template_name, context)

    def post(self, request: HttpRequest) -> HttpResponse:
        user = request.user
        context = {"user": user, "role": user.role}

        if user.role == UserRole.STUDENT:
            # Enforce strictly on the current user's profile instance
            student_profile, _ = StudentProfile.objects.get_or_create(user=user)
            form = StudentSelfProfileForm(
                request.POST, request.FILES, instance=student_profile
            )
            if form.is_valid():
                form.save()
                # Also allow updating phone number from request if provided
                new_phone = request.POST.get("phone_number")
                if new_phone is not None:
                    user.phone_number = new_phone
                    user.save(update_fields=["phone_number"])

                messages.success(request, _("Your student profile has been updated successfully."))
                return redirect("accounts:profile")
            else:
                context["student_profile"] = student_profile
                context["form"] = form
                return render(request, self.template_name, context)

        elif user.role == UserRole.FACULTY:
            # Enforce strictly on the current user's faculty profile instance
            faculty_profile, _ = FacultyProfile.objects.get_or_create(user=user)
            form = FacultySelfProfileForm(
                request.POST, request.FILES, instance=faculty_profile
            )
            if form.is_valid():
                form.save()
                new_phone = request.POST.get("phone_number")
                if new_phone is not None:
                    user.phone_number = new_phone
                    user.save(update_fields=["phone_number"])

                messages.success(request, _("Your faculty profile has been updated successfully."))
                return redirect("accounts:profile")
            else:
                context["faculty_profile"] = faculty_profile
                context["form"] = form
                return render(request, self.template_name, context)

        else:
            messages.info(request, _("Staff and Super Admin profiles are managed via the Django Admin."))
            return redirect("accounts:profile")
