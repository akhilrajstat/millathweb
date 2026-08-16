"""
apps/accounts/admin.py
=======================
Django admin configuration for custom User and StudentProfile models,
including bulk user approval with automated email notification, friendly help texts,
and photo previews.
"""

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.mail import send_mail
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_image_file
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
            _("ERP Profile & Role"),
            {
                "fields": ("role", "phone_number", "is_approved"),
                "description": _("Designate the user's role (Student, Faculty, Office Staff, Administrator) and account approval state."),
            },
        ),
    )

    # Also expose them when creating a new user via the admin.
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (
            _("ERP Profile & Role"),
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "role", "is_approved"),
                "description": _("Set initial user details and role."),
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


class StudentProfileAdminForm(forms.ModelForm):
    """Admin form for StudentProfile with friendly guidance and image validation."""

    class Meta:
        model = StudentProfile
        fields = "__all__"
        help_texts = {
            "user": _("Select the student user account linked to this academic profile."),
            "admission_number": _("Official institutional admission / registration number (e.g. 'BED-2026-042')."),
            "program": _("Academic program enrolled in (e.g. B.Ed, M.Ed)."),
            "batch_year": _("Admission batch year (e.g. '2025-2027')."),
            "date_of_birth": _("Student's date of birth (YYYY-MM-DD format)."),
            "photo": _("Student's passport-size identity photo (JPG/PNG format, under 5MB)."),
            "address": _("Residential or permanent postal address of the student."),
            "guardian_name": _("Full name of parent or legal guardian."),
            "guardian_phone": _("Emergency contact phone number for the guardian."),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "file"):
            validate_image_file(photo)
        return photo


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for StudentProfile management by office staff.
    """

    form = StudentProfileAdminForm
    list_display = (
        "photo_thumbnail",
        "get_student_name",
        "admission_number",
        "program",
        "batch_year",
        "guardian_phone",
    )
    list_display_links = ("photo_thumbnail", "get_student_name")
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
    readonly_fields = ("photo_preview",)

    fieldsets = (
        (
            _("Student Account"),
            {
                "fields": ("user",),
                "description": _("Associated student user account credentials."),
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
            _("Personal & Identity Photo"),
            {
                "fields": ("photo", "photo_preview", "date_of_birth", "address"),
                "description": _("Student's passport photo and personal residence details."),
            },
        ),
        (
            _("Guardian & Emergency Contacts"),
            {
                "fields": ("guardian_name", "guardian_phone"),
                "description": _("Parent or guardian emergency contact information."),
            },
        ),
    )

    @admin.display(description=_("Photo"))
    def photo_thumbnail(self, obj: StudentProfile):
        if obj and obj.photo:
            return format_html(
                '<img src="{}" alt="{}" style="width: 36px; height: 36px; border-radius: 50%; object-fit: cover; border: 1px solid #cbd5e1;" />',
                obj.photo.url,
                obj.user.get_full_name() or obj.user.username,
            )
        return format_html(
            '<div style="width: 36px; height: 36px; border-radius: 50%; background: #e2e8f0; display: flex; align-items: center; justify-content: center; color: #64748b; font-size: 11px; font-weight: 600;">{}</div>',
            ((obj.user.first_name[:1] + obj.user.last_name[:1]) if obj.user.first_name and obj.user.last_name else obj.user.username[:2]).upper(),
        )

    @admin.display(description=_("Student Name"), ordering="user__first_name")
    def get_student_name(self, obj: StudentProfile) -> str:
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description=_("Current Photo Preview"))
    def photo_preview(self, obj: StudentProfile):
        if obj and obj.photo:
            return format_html(
                '<div style="margin-top: 5px;">'
                '<img src="{}" alt="{}" style="max-height: 180px; max-width: 180px; object-fit: cover; border-radius: 8px; border: 1px solid #cbd5e1;" />'
                '</div>',
                obj.photo.url,
                obj.user.get_full_name() or obj.user.username,
            )
        return _("Upload a student photo above to see a preview.")
