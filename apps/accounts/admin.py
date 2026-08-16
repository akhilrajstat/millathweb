"""
apps/accounts/admin.py
=======================
Django admin configuration for custom User and StudentProfile models,
including bulk user approval with automated email notification.
"""

from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from .models import StudentProfile, User, UserRole


class StudentProfileInline(admin.StackedInline):
    """Inline editor for StudentProfile on the User change page."""

    model = StudentProfile
    can_delete = False
    verbose_name_plural = _("Student Profile Details")
    fk_name = "user"
    extra = 0
    classes = ("collapse",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for the custom User model with bulk approval action."""

    list_display = (
        "username",
        "email",
        "get_full_name",
        "role",
        "is_approved",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "is_approved", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name", "phone_number")
    ordering = ("last_name", "first_name")
    actions = ["approve_selected_users"]

    # Add custom fields to the fieldsets shown on the change form.
    fieldsets = BaseUserAdmin.fieldsets + (
        (
            _("ERP Profile"),
            {
                "fields": ("role", "phone_number", "is_approved"),
            },
        ),
    )

    # Also expose them when creating a new user via the admin.
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("ERP Profile"),
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "role", "is_approved"),
            },
        ),
    )

    inlines = [StudentProfileInline]

    @admin.action(description=_("Approve selected users and notify via email"))
    def approve_selected_users(self, request, queryset):
        """
        Bulk action: sets is_approved=True and sends an email notification
        with the login URL to each approved user.
        """
        unapproved_users = queryset.filter(is_approved=False)
        count = unapproved_users.count()

        if count == 0:
            self.message_user(
                request,
                _("All selected users are already approved."),
                level=messages.INFO,
            )
            return

        login_url = request.build_absolute_uri("/accounts/login/")

        for user in unapproved_users:
            user.is_approved = True
            user.save(update_fields=["is_approved"])

            # Send email confirmation
            if user.email:
                subject = "Your Millath College ERP Account Has Been Approved"
                message_body = (
                    f"Dear {user.get_full_name() or user.username},\n\n"
                    f"Your account ({user.get_role_display()}) for Millath College ERP has been reviewed "
                    f"and approved by the administration.\n\n"
                    f"You may now sign in to your dashboard at:\n"
                    f"{login_url}\n\n"
                    f"Username: {user.username}\n"
                    f"Email: {user.email}\n\n"
                    f"If you have any questions or require assistance, please contact the administrative office.\n\n"
                    f"—\n"
                    f"Administration Desk\n"
                    f"Millath College of Education"
                )
                send_mail(
                    subject=subject,
                    message=message_body,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@millathcollege.edu.in"),
                    recipient_list=[user.email],
                    fail_silently=True,
                )

        self.message_user(
            request,
            _(f"Successfully approved {count} user account(s) and dispatched email notifications."),
            level=messages.SUCCESS,
        )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for StudentProfile management by office staff.
    """

    list_display = (
        "get_student_name",
        "admission_number",
        "program",
        "batch_year",
        "guardian_phone",
    )
    list_filter = ("program", "batch_year")
    search_fields = (
        "admission_number",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "guardian_name",
    )
    ordering = ("user__last_name", "user__first_name")

    fieldsets = (
        (
            _("Student Account"),
            {
                "fields": ("user",),
                "description": _("Associated student user account."),
            },
        ),
        (
            _("Academic Enrollment (Office Staff Only)"),
            {
                "fields": ("admission_number", "program", "batch_year"),
                "description": _("Enrollment credentials assigned by college office staff."),
            },
        ),
        (
            _("Personal & Guardian Information"),
            {
                "fields": ("date_of_birth", "photo", "address", "guardian_name", "guardian_phone"),
                "description": _("Student's personal details and guardian emergency contacts."),
            },
        ),
    )

    @admin.display(description=_("Student Name"), ordering="user__first_name")
    def get_student_name(self, obj: StudentProfile) -> str:
        return obj.user.get_full_name() or obj.user.username
