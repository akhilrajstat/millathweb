"""
apps/assignments/views.py
=========================
Secure views for assignment management, student file submissions, and faculty grading.
Enforces strict queryset-level authorization across all endpoints.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.accounts.models import UserRole
from apps.assignments.forms import AssignmentForm, GradeSubmissionForm, SubmissionForm
from apps.assignments.models import Assignment, Submission


class AssignmentListView(LoginRequiredMixin, ListView):
    """
    Displays coursework assignments tailored strictly to user role:
    - Students see active assignments matching their enrolled academic program.
    - Faculty see assignments they personally created.
    - Office staff and administrators can view all assignments for oversight.
    """

    model = Assignment
    template_name = "assignments/list.html"
    context_object_name = "assignments"
    paginate_by = 15
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]:
            return Assignment.objects.all().select_related("created_by", "program").order_by("-due_date")

        if user.role == UserRole.FACULTY:
            return Assignment.objects.filter(created_by=user).select_related("program").order_by("-due_date")

        # Student role: show active assignments scoped to their program or global assignments
        student_prog = None
        if hasattr(user, "student_profile") and user.student_profile and user.student_profile.program:
            student_prog = user.student_profile.program

        if student_prog:
            queryset = Assignment.objects.filter(
                is_active=True
            ).filter(
                Q(program__isnull=True) | Q(program=student_prog)
            )
        else:
            queryset = Assignment.objects.filter(is_active=True)

        return queryset.select_related("created_by", "program").order_by("-due_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # For students, pre-build a map of their submission status for the assignments on page
        if user.role == UserRole.STUDENT:
            assignments = context["assignments"]
            assignment_ids = [a.id for a in assignments]
            user_submissions = {
                sub.assignment_id: sub
                for sub in Submission.objects.filter(assignment_id__in=assignment_ids, student=user)
            }
            context["user_submissions"] = user_submissions

        context["is_faculty"] = user.role == UserRole.FACULTY or user.is_superuser
        context["is_student"] = user.role == UserRole.STUDENT
        context["can_create"] = (
            user.role == UserRole.FACULTY
            or user.is_superuser
            or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]
        )
        return context


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    """
    Displays full assignment details.
    - Students see instructions + their own submission status/grade.
    - Faculty see instructions + full submission roster for assignments they created.
    """

    model = Assignment
    template_name = "assignments/detail.html"
    context_object_name = "assignment"
    login_url = reverse_lazy("accounts:login")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]:
            return Assignment.objects.all().select_related("created_by", "program")

        if user.role == UserRole.FACULTY:
            # Faculty can only view assignments they created
            return Assignment.objects.filter(created_by=user).select_related("created_by", "program")

        # Student: active assignments matching their program or global
        student_prog = None
        if hasattr(user, "student_profile") and user.student_profile and user.student_profile.program:
            student_prog = user.student_profile.program

        if student_prog:
            return Assignment.objects.filter(
                is_active=True
            ).filter(
                Q(program__isnull=True) | Q(program=student_prog)
            ).select_related("created_by", "program")
        return Assignment.objects.filter(is_active=True).select_related("created_by", "program")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        user = self.request.user

        if user.role == UserRole.STUDENT:
            # Strict isolation: retrieve ONLY this student's own submission
            context["student_submission"] = Submission.objects.filter(
                assignment=assignment,
                student=user
            ).select_related("graded_by").first()
            context["can_submit"] = not assignment.is_past_due and assignment.is_active

        elif user.role == UserRole.FACULTY or user.is_superuser or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]:
            # Faculty/staff oversight: load all submissions under this assignment
            context["submissions_list"] = assignment.submissions.select_related(
                "student",
                "student__student_profile",
                "graded_by"
            ).order_by("-submitted_at")
            context["total_submissions"] = assignment.submissions.count()
            context["graded_count"] = assignment.submissions.filter(marks_obtained__isnull=False).count()
            context["pending_count"] = assignment.submissions.filter(marks_obtained__isnull=True).count()

        context["is_creator"] = (assignment.created_by == user) or user.is_superuser
        context["is_student"] = user.role == UserRole.STUDENT
        context["is_faculty"] = user.role == UserRole.FACULTY or user.is_superuser
        return context


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Allows faculty and administrators to author a new coursework assignment.
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/form.html"
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return (
            user.is_superuser
            or user.role in [UserRole.FACULTY, UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]
        )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            _(f"Assignment '{form.instance.title}' has been successfully published."),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Create Coursework Assignment")
        context["submit_button_text"] = _("Publish Assignment")
        return context


class AssignmentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows faculty to edit assignments they originally created.
    """

    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/form.html"
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        assignment = self.get_object()
        return user.is_superuser or assignment.created_by == user

    def form_valid(self, form):
        messages.success(
            self.request,
            _(f"Assignment '{form.instance.title}' was successfully updated."),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _(f"Edit Assignment: {self.object.title}")
        context["submit_button_text"] = _("Save Changes")
        context["is_edit"] = True
        return context


class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows faculty to delete assignments they originally created.
    """

    model = Assignment
    template_name = "assignments/confirm_delete.html"
    success_url = reverse_lazy("assignments:list")
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        assignment = self.get_object()
        return user.is_superuser or assignment.created_by == user

    def form_valid(self, form):
        messages.success(
            self.request,
            _(f"Assignment '{self.object.title}' has been permanently deleted."),
        )
        return super().form_valid(form)


class SubmissionSubmitView(LoginRequiredMixin, View):
    """
    Unified view handling both initial submission and resubmissions by enrolled students.
    Enforces strict deadline verification and updates existing records idempotently.
    """

    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        # Ensure only student role or superadmin can submit coursework
        if request.user.role != UserRole.STUDENT and not request.user.is_superuser:
            return HttpResponseForbidden("403 Forbidden: Only registered students can submit coursework.")

        return super().dispatch(request, *args, **kwargs)

    def get_assignment(self, assignment_id: int) -> Assignment:
        assignment = get_object_or_404(Assignment, pk=assignment_id, is_active=True)

        # Verify student's academic program eligibility if scoped
        user = self.request.user
        if assignment.program and not user.is_superuser:
            student_prog = getattr(getattr(user, "student_profile", None), "program", None)
            if student_prog and student_prog != assignment.program:
                raise Http404("Assignment is not applicable to your academic program.")

        return assignment

    def get(self, request: HttpRequest, assignment_id: int) -> HttpResponse:
        assignment = self.get_assignment(assignment_id)

        # Check deadline
        if assignment.is_past_due:
            messages.error(
                request,
                _(f"Submission closed: The deadline for '{assignment.title}' expired on "
                  f"{assignment.due_date.strftime('%b %d, %Y at %I:%M %p')}."),
            )
            return redirect("assignments:detail", pk=assignment.pk)

        # Check existing submission
        existing_submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()

        form = SubmissionForm(instance=existing_submission) if existing_submission else SubmissionForm()

        return render(
            request,
            "assignments/submit.html",
            {
                "assignment": assignment,
                "form": form,
                "existing_submission": existing_submission,
                "is_resubmission": existing_submission is not None,
            },
        )

    def post(self, request: HttpRequest, assignment_id: int) -> HttpResponse:
        assignment = self.get_assignment(assignment_id)

        # Strict deadline enforcement on POST
        if assignment.is_past_due:
            messages.error(
                request,
                _(f"Submission rejected: The deadline for this assignment expired on "
                  f"{assignment.due_date.strftime('%b %d, %Y at %I:%M %p')}."),
            )
            return redirect("assignments:detail", pk=assignment.pk)

        existing_submission = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).first()

        if existing_submission:
            form = SubmissionForm(request.POST, request.FILES, instance=existing_submission)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.submitted_at = timezone.now()
                # If resubmitting, clear prior marks & feedback to trigger fresh review
                submission.marks_obtained = None
                submission.feedback = ""
                submission.graded_at = None
                submission.graded_by = None
                submission.save()

                messages.success(
                    request,
                    _("Your assignment has been resubmitted successfully. It is now awaiting faculty evaluation."),
                )
                return redirect("assignments:detail", pk=assignment.pk)
        else:
            form = SubmissionForm(request.POST, request.FILES)
            if form.is_valid():
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.save()

                messages.success(
                    request,
                    _("Your assignment has been submitted successfully!"),
                )
                return redirect("assignments:detail", pk=assignment.pk)

        return render(
            request,
            "assignments/submit.html",
            {
                "assignment": assignment,
                "form": form,
                "existing_submission": existing_submission,
                "is_resubmission": existing_submission is not None,
            },
        )


class GradeSubmissionView(LoginRequiredMixin, View):
    """
    Faculty evaluation view: Allows instructors to award marks and write feedback.
    Strictly isolated at queryset level so faculty can ONLY grade submissions under
    assignments they personally created.
    """

    login_url = reverse_lazy("accounts:login")

    def get_submission(self, pk: int) -> Submission:
        user = self.request.user
        if user.is_superuser or user.role in [UserRole.SUPER_ADMIN, UserRole.OFFICE_STAFF]:
            return get_object_or_404(
                Submission.objects.select_related("assignment", "student", "student__student_profile"),
                pk=pk
            )

        if user.role == UserRole.FACULTY:
            return get_object_or_404(
                Submission.objects.filter(assignment__created_by=user).select_related(
                    "assignment", "student", "student__student_profile"
                ),
                pk=pk
            )

        raise Http404("You do not have permission to evaluate this submission.")

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        submission = self.get_submission(pk)
        form = GradeSubmissionForm(
            instance=submission,
            assignment_max_marks=submission.assignment.max_marks
        )
        return render(
            request,
            "assignments/grade.html",
            {
                "submission": submission,
                "assignment": submission.assignment,
                "form": form,
            },
        )

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        submission = self.get_submission(pk)
        form = GradeSubmissionForm(
            request.POST,
            instance=submission,
            assignment_max_marks=submission.assignment.max_marks
        )
        if form.is_valid():
            graded = form.save(commit=False)
            graded.graded_at = timezone.now()
            graded.graded_by = request.user
            graded.save()

            student_name = submission.student.get_full_name() or submission.student.username
            messages.success(
                request,
                _(f"Grading completed for {student_name}: Awarded {graded.marks_obtained}/{submission.assignment.max_marks} marks."),
            )
            return redirect("assignments:detail", pk=submission.assignment.pk)

        return render(
            request,
            "assignments/grade.html",
            {
                "submission": submission,
                "assignment": submission.assignment,
                "form": form,
            },
        )
