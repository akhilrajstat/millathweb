"""
apps/assignments/tests.py
=========================
Unit tests and permission/IDOR integration tests for Assignments and Submissions.
"""

from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User, UserRole, StudentProfile
from apps.assignments.models import Assignment, Submission
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
class AssignmentModuleTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Programs
        self.program_math = Program.objects.create(
            name="B.Ed - Mathematics",
            description="Math Program",
            duration="2 Years",
            eligibility="Graduation in Math",
            is_active=True,
        )
        self.program_english = Program.objects.create(
            name="B.Ed - English",
            description="English Program",
            duration="2 Years",
            eligibility="Graduation in English",
            is_active=True,
        )

        # Faculty 1 (Creator)
        self.faculty1 = User.objects.create_user(
            username="faculty1",
            email="faculty1@millath.edu",
            password="Password123!",
            role=UserRole.FACULTY,
            is_approved=True,
            first_name="Bindu",
            last_name="Kumari",
        )

        # Faculty 2 (Other instructor)
        self.faculty2 = User.objects.create_user(
            username="faculty2",
            email="faculty2@millath.edu",
            password="Password123!",
            role=UserRole.FACULTY,
            is_approved=True,
            first_name="Suba",
            last_name="Basheer",
        )

        # Student 1 (Enrolled in Math)
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
            program=self.program_math,
        )

        # Student 2 (Enrolled in English)
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
            program=self.program_english,
        )

        # Active Assignment created by Faculty 1 for Math Program
        self.assignment_math = Assignment.objects.create(
            title="Algebra Methodology Assignment",
            description="<p>Submit solutions to Unit 1 exercises.</p>",
            created_by=self.faculty1,
            program=self.program_math,
            due_date=timezone.now() + timedelta(days=7),
            max_marks=100,
            is_active=True,
        )

        # Past-due Assignment created by Faculty 1
        self.assignment_expired = Assignment.objects.create(
            title="Past Due Geometry Task",
            description="<p>Expired task.</p>",
            created_by=self.faculty1,
            program=self.program_math,
            due_date=timezone.now() - timedelta(days=2),
            max_marks=50,
            is_active=True,
        )

    def test_assignment_model_properties(self):
        """Test properties and calculations on Assignment model."""
        self.assertFalse(self.assignment_math.is_past_due)
        self.assertTrue(self.assignment_expired.is_past_due)
        self.assertEqual(self.assignment_math.total_submissions, 0)
        self.assertEqual(self.assignment_math.graded_submissions_count, 0)

    def test_student_assignment_list_scoping(self):
        """Test that students only see active assignments relevant to their program or global."""
        self.client.force_login(self.student1)
        response = self.client.get(reverse("assignments:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Algebra Methodology Assignment")

        # Student 2 (English) should not see Math assignment
        self.client.force_login(self.student2)
        response = self.client.get(reverse("assignments:list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Algebra Methodology Assignment")

    def test_student_submission_creation_and_resubmission(self):
        """Test that a student can upload a submission and resubmission updates the record idempotently."""
        self.client.force_login(self.student1)

        upload_file1 = SimpleUploadedFile("solution1.pdf", b"%PDF-1.4 dummy content", content_type="application/pdf")
        submit_url = reverse("assignments:submit", kwargs={"assignment_id": self.assignment_math.pk})

        response = self.client.post(submit_url, {"submitted_file": upload_file1}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify submission created
        self.assertEqual(Submission.objects.filter(assignment=self.assignment_math, student=self.student1).count(), 1)
        sub = Submission.objects.get(assignment=self.assignment_math, student=self.student1)
        self.assertFalse(sub.is_graded)

        # Faculty 1 grades the submission
        sub.marks_obtained = 90
        sub.feedback = "Good job!"
        sub.graded_at = timezone.now()
        sub.graded_by = self.faculty1
        sub.save()

        self.assertEqual(sub.percentage, 90.0)

        # Student 1 resubmits a revised file
        upload_file2 = SimpleUploadedFile("solution2.docx", b"dummy word content", content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response = self.client.post(submit_url, {"submitted_file": upload_file2}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Ensure NO duplicate was created (still count == 1) and previous grade is reset for fresh review
        self.assertEqual(Submission.objects.filter(assignment=self.assignment_math, student=self.student1).count(), 1)
        sub.refresh_from_db()
        self.assertIsNone(sub.marks_obtained)
        self.assertFalse(sub.is_graded)

    def test_past_due_submission_rejection(self):
        """Test that students cannot submit coursework to an expired assignment."""
        self.client.force_login(self.student1)
        upload_file = SimpleUploadedFile("late.pdf", b"%PDF-1.4 dummy content", content_type="application/pdf")
        submit_url = reverse("assignments:submit", kwargs={"assignment_id": self.assignment_expired.pk})

        response = self.client.post(submit_url, {"submitted_file": upload_file}, follow=True)
        self.assertEqual(response.status_code, 200)

        # Verify no submission was recorded
        self.assertEqual(Submission.objects.filter(assignment=self.assignment_expired, student=self.student1).count(), 0)

    def test_faculty_grading_permissions_and_idor_protection(self):
        """Test that only the creating faculty can grade submissions under their assignment."""
        # Create a submission by student1
        sub = Submission.objects.create(
            assignment=self.assignment_math,
            student=self.student1,
            submitted_file=SimpleUploadedFile("work.pdf", b"dummy content"),
        )

        grade_url = reverse("assignments:grade", kwargs={"pk": sub.pk})

        # Faculty 2 attempts to grade Faculty 1's assignment submission -> Should get 404
        self.client.force_login(self.faculty2)
        response = self.client.get(grade_url)
        self.assertEqual(response.status_code, 404)

        # Student 1 attempts to access grade endpoint directly -> 404
        self.client.force_login(self.student1)
        response = self.client.get(grade_url)
        self.assertEqual(response.status_code, 404)

        # Faculty 1 (the legitimate creator) grades the submission -> Success 200 / redirect
        self.client.force_login(self.faculty1)
        response = self.client.post(
            grade_url,
            {"marks_obtained": 95, "feedback": "Excellent methodology and neat derivations."},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        sub.refresh_from_db()
        self.assertEqual(sub.marks_obtained, 95)
        self.assertEqual(sub.percentage, 95.0)
        self.assertEqual(sub.graded_by, self.faculty1)
        self.assertTrue(sub.is_graded)
