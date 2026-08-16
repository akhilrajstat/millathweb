"""
apps/accounts/models.py
========================
Custom User model for Millath College ERP.

Design notes
------------
* Roles are defined as a TextChoices enum (UserRole) so that the role
  strings are declared ONCE and referenced by name everywhere — no raw
  strings scattered across the codebase.
* email is made required and unique (replaces username as the login
  identifier in the admin; standard LoginView still uses username/email
  depending on the form used — this is configurable per-view).
* is_approved (default False) lets staff gate access before a user can
  log in, enforced at the authentication layer in views.py.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.validators import validate_file_size_5mb


class UserRole(models.TextChoices):
    """Exhaustive list of roles in the ERP system.

    Add new roles here ONLY — never use raw strings elsewhere.
    """

    SUPER_ADMIN = "super_admin", _("Super Admin")
    PRINCIPAL = "principal", _("Principal")
    OFFICE_STAFF = "office_staff", _("Office Staff")
    FACULTY = "faculty", _("Faculty")
    STUDENT = "student", _("Student")


class User(AbstractUser):
    """
    Custom user model that replaces Django's default User.

    Extra fields
    ------------
    role          : The user's role in the ERP (from UserRole choices).
    phone_number  : Optional contact number.
    is_approved   : Whether an admin has approved this account for login.
                    Defaults to False so new self-registrations are gated.
    """

    # Make email required and unique so it can serve as a natural identifier.
    email = models.EmailField(
        _("email address"),
        unique=True,
        help_text=_("Required. Must be unique across all users."),
    )

    role = models.CharField(
        _("role"),
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        db_index=True,
        help_text=_("The user's functional role within the ERP."),
    )

    phone_number = models.CharField(
        _("phone number"),
        max_length=20,
        blank=True,
        help_text=_("Optional. Include country code for international numbers."),
    )

    is_approved = models.BooleanField(
        _("approved"),
        default=False,
        help_text=_(
            "Designates whether this account has been approved by an administrator. "
            "Users cannot log in until this is True."
        ),
    )

    # Keep username as the USERNAME_FIELD default (Django requirement for
    # AbstractUser) but add email to REQUIRED_FIELDS so createsuperuser prompts for it.
    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["last_name", "first_name"]

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.is_approved = True
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        full_name = self.get_full_name() or self.username
        role_label = self.get_role_display()
        return f"{full_name} ({role_label})"

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def is_super_admin(self) -> bool:
        return self.role == UserRole.SUPER_ADMIN

    @property
    def is_principal(self) -> bool:
        return self.role == UserRole.PRINCIPAL

    @property
    def is_office_staff(self) -> bool:
        return self.role == UserRole.OFFICE_STAFF

    @property
    def is_faculty(self) -> bool:
        return self.role == UserRole.FACULTY

    @property
    def is_student(self) -> bool:
        return self.role == UserRole.STUDENT


class StudentProfile(models.Model):
    """
    Student profile containing academic and personal contact information.
    Linked OneToOne with User where role is Student.
    """

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="student_profile",
        limit_choices_to={"role": UserRole.STUDENT},
        verbose_name=_("user account"),
    )
    admission_number = models.CharField(
        _("admission number"),
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text=_("Official roll / admission number assigned by office staff after approval."),
    )
    date_of_birth = models.DateField(
        _("date of birth"),
        null=True,
        blank=True,
        help_text=_("Student's date of birth (YYYY-MM-DD)."),
    )
    batch_year = models.CharField(
        _("batch year"),
        max_length=20,
        blank=True,
        help_text=_("Academic batch session (e.g. '2024-2026')."),
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profiles",
        verbose_name=_("enrolled degree program"),
        help_text=_("The academic program the student is enrolled in."),
    )
    photo = models.ImageField(
        _("passport photo"),
        upload_to="students/photos/",
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
                message=_("Allowed image formats are JPG, JPEG, PNG, or WEBP."),
            ),
            validate_file_size_5mb,
        ],
        help_text=_("Passport-sized photograph (max 5MB, JPG/PNG/WEBP)."),
    )
    address = models.TextField(
        _("permanent / residential address"),
        blank=True,
        help_text=_("Student's current mailing or home address."),
    )
    guardian_name = models.CharField(
        _("guardian / parent name"),
        max_length=150,
        blank=True,
        help_text=_("Full name of parent or legal guardian."),
    )
    guardian_phone = models.CharField(
        _("guardian contact number"),
        max_length=20,
        blank=True,
        help_text=_("Primary contact phone number of guardian."),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("Student Profile")
        verbose_name_plural = _("Student Profiles")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        adm = f" [{self.admission_number}]" if self.admission_number else " [Pending ID]"
        return f"{self.user.get_full_name() or self.user.username}{adm}"

