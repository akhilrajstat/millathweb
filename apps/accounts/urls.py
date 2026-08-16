"""
apps/accounts/urls.py
======================
URL patterns for authentication and account management.

Includes
--------
* Login / Logout
* Django's built-in password-reset flow (4 views)
* Dashboard (authenticated landing page)
"""

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------
    path(
        "login/",
        views.CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "register/",
        views.RegisterView.as_view(),
        name="register",
    ),
    path(
        "profile/",
        views.ProfileView.as_view(),
        name="profile",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="accounts:login"),
        name="logout",
    ),

    # ------------------------------------------------------------------
    # Password reset flow (all Django built-ins)
    # ------------------------------------------------------------------
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="accounts/emails/password_reset_email.txt",
            subject_template_name="accounts/emails/password_reset_subject.txt",
            success_url="done/",
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html",
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url="/accounts/password-reset/complete/",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html",
        ),
        name="password_reset_complete",
    ),

    # ------------------------------------------------------------------
    # Authenticated pages
    # ------------------------------------------------------------------
    path(
        "dashboard/",
        views.DashboardView.as_view(),
        name="dashboard",
    ),
]
