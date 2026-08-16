"""
apps/accounts/forms.py
======================
Forms for user self-registration and self-service profile editing.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.widgets import CKEditor5Widget

from apps.accounts.models import StudentProfile, UserRole
from apps.faculty.models import FacultyProfile

User = get_user_model()


class RegistrationForm(forms.Form):
    """
    Public self-registration form for prospective Students and Faculty.
    Restricted to Student and Faculty roles only.
    """

    ALLOWED_ROLES = [
        (UserRole.STUDENT.value, _("Student")),
        (UserRole.FACULTY.value, _("Faculty")),
    ]

    role = forms.ChoiceField(
        choices=ALLOWED_ROLES,
        label=_("Register As"),
        widget=forms.Select(attrs={"class": "form-select", "id": "reg_role"}),
        help_text=_("Select whether you are joining as a Student or Faculty member."),
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label=_("First Name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        label=_("Last Name"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last name"}),
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        label=_("Username"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username", "autocomplete": "username"}),
        help_text=_("Letters, digits and @/./+/-/_ only."),
    )
    email = forms.EmailField(
        required=True,
        label=_("Email Address"),
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com", "autocomplete": "email"}),
        help_text=_("Required for notifications and password recovery."),
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label=_("Phone Number"),
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 98765 43210"}),
    )
    password_1 = forms.CharField(
        required=True,
        label=_("Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Minimum 10 characters", "autocomplete": "new-password"}),
        help_text=_("Must be at least 10 characters and cannot be too common."),
    )
    password_2 = forms.CharField(
        required=True,
        label=_("Confirm Password"),
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Re-enter password", "autocomplete": "new-password"}),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError(_("A user with this username already exists."))
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("An account with this email address already exists."))
        return email

    def clean(self):
        cleaned_data = super().clean()
        password_1 = cleaned_data.get("password_1")
        password_2 = cleaned_data.get("password_2")

        if password_1 and password_2:
            if password_1 != password_2:
                self.add_error("password_2", _("The two password fields did not match."))
            else:
                # Apply Django's AUTH_PASSWORD_VALIDATORS
                user_instance = User(
                    username=cleaned_data.get("username", ""),
                    email=cleaned_data.get("email", ""),
                    first_name=cleaned_data.get("first_name", ""),
                    last_name=cleaned_data.get("last_name", ""),
                )
                try:
                    validate_password(password_1, user=user_instance)
                except ValidationError as error:
                    self.add_error("password_1", error)

        return cleaned_data

    def save(self) -> User:
        """Create inactive / unapproved User and associated profile."""
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password_1"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone_number=data.get("phone_number", ""),
            role=data["role"],
            is_approved=False,
        )

        if user.role == UserRole.STUDENT:
            StudentProfile.objects.get_or_create(user=user)
        elif user.role == UserRole.FACULTY:
            FacultyProfile.objects.get_or_create(
                user=user,
                defaults={
                    "designation": "Faculty Member",
                    "qualification": "Pending Verification",
                    "is_published": False,
                },
            )

        return user


class StudentSelfProfileForm(forms.ModelForm):
    """
    Form for approved students to manage their personal profile info.
    Restricted: Cannot edit admission_number, batch_year, or program.
    """

    class Meta:
        model = StudentProfile
        fields = [
            "photo",
            "date_of_birth",
            "address",
            "guardian_name",
            "guardian_phone",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Enter your current residential address"}),
            "guardian_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Guardian / Parent name"}),
            "guardian_phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 9876543210"}),
        }


class FacultySelfProfileForm(forms.ModelForm):
    """
    Form for approved faculty members to manage their biographical details.
    Restricted: Cannot edit designation or publishing status.
    """

    class Meta:
        model = FacultyProfile
        fields = [
            "photo",
            "qualification",
            "specialization",
            "email_display",
            "bio",
        ]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "qualification": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. M.Ed., Ph.D., UGC-NET"}),
            "specialization": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Mathematics Pedagogy, EdTech"}),
            "email_display": forms.EmailInput(attrs={"class": "form-control", "placeholder": "public.email@millathcollege.edu.in"}),
            "bio": CKEditor5Widget(config_name="extends"),
        }
