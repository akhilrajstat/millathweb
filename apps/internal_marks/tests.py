"""
apps/internal_marks/tests.py
============================
Unit tests and permission/IDOR integration tests for the Internal Assessment Marks module.
"""

from django.core.exceptions import ValidationError
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import StudentProfile, User, UserRole
from apps.internal_marks.models import InternalMark, MarkStatus
from apps.programs.models import Program


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
    }
)
class InternalMarksModuleTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Academic Program
        self.program = Program.objects.create(
            name="B.Ed - Mathematics",
            description="Math Program",
            duration="2 Years",
            eligibility="Graduation in Math",
            is_active=True,
        )

        # Principal User
        self.principal = User.objects.create_user(
            username="principal_user",
            email="principal@millath.edu",
            password="Password123!",
            role=UserRole.PRINCIPAL,
            is_approved=True,
            first_name="Dr. K.",
            last_name="Principal",
        )

        # Faculty 1 User (Evaluating instructor)
        self.faculty1 = User.objects.create_user(
            username="faculty1",
            email="faculty1@millath.edu",
            password="Password123!",
            role=UserRole.FACULTY,
            is_approved=True,
            first_name="Bindu",
            last_name="Kumari",
        )

        # Faculty 2 User (Other instructor)
        self.faculty2 = User.objects.create_user(
            username="faculty2",
            email="faculty2@millath.edu",
            password="Password123!",
            role=UserRole.FACULTY,
            is_approved=True,
            first_name="Suba",
            last_name="Basheer",
        )

        # Office Staff User
        self.office_staff = User.objects.create_user(
            username="staff_user",
            email="staff@millath.edu",
            password="Password123!",
            role=UserRole.OFFICE_STAFF,
            is_approved=True,
            first_name="Saritha",
            last_name="K.R",
        )

        # Student 1 User
        self.student1 = User.objects.create_user(
            username="student1",
            email="student1@millath.edu",
            password="Password123!",
            role=UserRole.STUDENT,
            is_approved=True,
            first_name="Rahul",
            last_name="Nair",
        )
        self.profile1 = StudentProfile.objects.create(
            user=self.student1,
            admission_number="ADM-2026-001",
            program=self.program,
        )

        # Student 2 User
        self.student2 = User.objects.create_user(
            username="student2",
            email="student2@millath.edu",
            password="Password123!",
            role=UserRole.STUDENT,
            is_approved=True,
            first_name="Ananya",
            last_name="Das",
        )
        self.profile2 = StudentProfile.objects.create(
            user=self.student2,
            admission_number="ADM-2026-002",
            program=self.program,
        )

    def test_model_validation_exceeded_marks(self):
        """Test that model clean() prevents marks_obtained > max_marks."""
        invalid_mark = InternalMark(
            student=self.student1,
            program=self.program,
            subject="Pedagogy of Mathematics",
            max_marks=20,
            marks_obtained=25,  # Exceeds max_marks
            entered_by=self.faculty1,
        )
        with self.assertRaises(ValidationError):
            invalid_mark.full_clean()

    def test_faculty_mark_creation_and_editing_workflow(self):
        """Test faculty can create and edit draft marks entered by self."""
        self.client.force_login(self.faculty1)

        # 1. Create a draft mark entry
        create_url = reverse("internal_marks:create")
        response = self.client.post(
            create_url,
            {
                "student": self.student1.pk,
                "program": self.program.pk,
                "subject": "Algebra Methodology",
                "max_marks": 20,
                "marks_obtained": 18,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        mark = InternalMark.objects.get(student=self.student1, subject="Algebra Methodology")
        self.assertEqual(mark.status, MarkStatus.DRAFT)
        self.assertEqual(mark.percentage, 90.0)
        self.assertEqual(mark.entered_by, self.faculty1)

        # 2. Faculty 1 updates the draft
        edit_url = reverse("internal_marks:edit", kwargs={"pk": mark.pk})
        response = self.client.post(
            edit_url,
            {
                "student": self.student1.pk,
                "program": self.program.pk,
                "subject": "Algebra Methodology",
                "max_marks": 20,
                "marks_obtained": 19,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        mark.refresh_from_db()
        self.assertEqual(mark.marks_obtained, 19)

        # 3. Faculty 2 attempts to edit Faculty 1's draft -> 404 (IDOR safe)
        self.client.force_login(self.faculty2)
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

    def test_full_approval_and_publishing_lifecycle(self):
        """Test complete workflow: Draft -> Submitted -> Approved -> Published."""
        # Create draft mark
        mark = InternalMark.objects.create(
            student=self.student1,
            program=self.program,
            subject="Pedagogy Unit 1",
            max_marks=20,
            marks_obtained=17,
            entered_by=self.faculty1,
            status=MarkStatus.DRAFT,
        )

        # Faculty submits for review
        self.client.force_login(self.faculty1)
        submit_url = reverse("internal_marks:submit_for_review", kwargs={"pk": mark.pk})
        response = self.client.post(submit_url, follow=True)
        self.assertEqual(response.status_code, 200)

        mark.refresh_from_db()
        self.assertEqual(mark.status, MarkStatus.SUBMITTED)

        # Faculty cannot edit submitted marks anymore -> 404
        edit_url = reverse("internal_marks:edit", kwargs={"pk": mark.pk})
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 404)

        # Principal reviews and approves marks
        self.client.force_login(self.principal)
        review_url = reverse("internal_marks:review", kwargs={"pk": mark.pk})
        response = self.client.post(
            review_url,
            {"action": "approve", "review_comment": "Verified and approved."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        mark.refresh_from_db()
        self.assertEqual(mark.status, MarkStatus.APPROVED)
        self.assertEqual(mark.reviewed_by, self.principal)

        # Student cannot see approved-but-unpublished mark
        self.client.force_login(self.student1)
        response = self.client.get(reverse("internal_marks:student_marks"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pedagogy Unit 1")

        # Principal publishes the approved mark
        self.client.force_login(self.principal)
        publish_url = reverse("internal_marks:publish", kwargs={"pk": mark.pk})
        response = self.client.post(publish_url, follow=True)
        self.assertEqual(response.status_code, 200)

        mark.refresh_from_db()
        self.assertEqual(mark.status, MarkStatus.PUBLISHED)
        self.assertIsNotNone(mark.published_at)

        # Student 1 now sees their published mark
        self.client.force_login(self.student1)
        response = self.client.get(reverse("internal_marks:student_marks"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pedagogy Unit 1")
        self.assertContains(response, "17")

        # Student 2 cannot see Student 1's mark
        self.client.force_login(self.student2)
        response = self.client.get(reverse("internal_marks:student_marks"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Pedagogy Unit 1")

    def test_rejection_and_resubmission_flow(self):
        """Test Principal rejecting mark with required feedback, allowing faculty revision."""
        mark = InternalMark.objects.create(
            student=self.student1,
            program=self.program,
            subject="Statistics",
            max_marks=20,
            marks_obtained=14,
            entered_by=self.faculty1,
            status=MarkStatus.SUBMITTED,
        )

        # Principal attempts to reject without a comment -> validation error
        self.client.force_login(self.principal)
        review_url = reverse("internal_marks:review", kwargs={"pk": mark.pk})
        response = self.client.post(
            review_url,
            {"action": "reject", "review_comment": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "review_comment", "A review comment is mandatory when rejecting marks to inform faculty what must be revised.")

        # Principal rejects with constructive feedback
        response = self.client.post(
            review_url,
            {"action": "reject", "review_comment": "Please recheck the assignment weightage score calculation."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        mark.refresh_from_db()
        self.assertEqual(mark.status, MarkStatus.REJECTED)
        self.assertEqual(mark.review_comment, "Please recheck the assignment weightage score calculation.")

        # Faculty can now edit the rejected mark
        self.client.force_login(self.faculty1)
        edit_url = reverse("internal_marks:edit", kwargs={"pk": mark.pk})
        response = self.client.post(
            edit_url,
            {
                "student": self.student1.pk,
                "program": self.program.pk,
                "subject": "Statistics",
                "max_marks": 20,
                "marks_obtained": 16,
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Faculty resubmits for review
        submit_url = reverse("internal_marks:submit_for_review", kwargs={"pk": mark.pk})
        response = self.client.post(submit_url, follow=True)
        self.assertEqual(response.status_code, 200)

        mark.refresh_from_db()
        self.assertEqual(mark.status, MarkStatus.SUBMITTED)
        self.assertEqual(mark.marks_obtained, 16)
        self.assertEqual(mark.review_comment, "")  # Cleared on resubmission

    def test_office_staff_access_restriction(self):
        """Test that office staff is rejected with 403 Forbidden on internal marks access."""
        self.client.force_login(self.office_staff)
        response = self.client.get(reverse("internal_marks:list"))
        self.assertEqual(response.status_code, 403)
