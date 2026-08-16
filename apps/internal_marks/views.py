"""
apps/internal_marks/views.py
============================
Secure views for internal assessment marks management, multi-stage review workflow,
and student grade publishing. Enforces strict role-based access control and IDOR protections.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.accounts.models import UserRole
from apps.internal_marks.forms import BulkPublishForm, InternalMarkForm, MarkReviewForm
from apps.internal_marks.models import InternalMark, MarkStatus
from apps.programs.models import Program


class MarkEntryListView(LoginRequiredMixin, ListView):
    """
    Role-aware listing of internal assessment records:
    - Faculty: sees only marks they personally entered.
    - Principal / Super Admin: sees submitted marks awaiting review (primary queue) plus all marks.
    - Student: redirected to StudentMarksView for their own published marks only.
    - Office Staff: rejected with 403 Forbidden.
    """

    model = InternalMark
    template_name = "internal_marks/list.html"
    context_object_name = "marks_list"
    paginate_by = 25
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        # Redirect student directly to student scorecard
        if request.user.role == UserRole.STUDENT:
            return redirect("internal_marks:student_marks")

        # Office staff restricted by default
        if request.user.role == UserRole.OFFICE_STAFF and not request.user.is_superuser:
            return HttpResponseForbidden(
                "403 Forbidden: Office staff do not have authorization to access internal mark management."
            )

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.GET.get("status", "").strip()
        program_filter = self.request.GET.get("program", "").strip()

        if user.is_superuser or user.role in [UserRole.PRINCIPAL, UserRole.SUPER_ADMIN]:
            queryset = InternalMark.objects.all().select_related("student", "student__student_profile", "program", "entered_by", "reviewed_by")
            # Default to submitted queue if no filter is explicitly applied
            if not status_filter:
                # If specifically requested 'all' via query param
                if self.request.GET.get("view") != "all":
                    queryset = queryset.filter(status=MarkStatus.SUBMITTED)
            elif status_filter in MarkStatus.values:
                queryset = queryset.filter(status=status_filter)

        elif user.role == UserRole.FACULTY:
            # Strictly scoped to records entered by this faculty member
            queryset = InternalMark.objects.filter(entered_by=user).select_related(
                "student", "student__student_profile", "program", "reviewed_by"
            )
            if status_filter in MarkStatus.values:
                queryset = queryset.filter(status=status_filter)
        else:
            raise PermissionDenied("You do not have permission to access internal marks.")

        if program_filter.isdigit():
            queryset = queryset.filter(program_id=int(program_filter))

        return queryset.order_by("-entered_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context["is_principal"] = user.is_superuser or user.role in [UserRole.PRINCIPAL, UserRole.SUPER_ADMIN]
        context["is_faculty"] = user.role == UserRole.FACULTY
        context["current_status"] = self.request.GET.get("status", "")
        context["current_program"] = self.request.GET.get("program", "")
        context["view_mode"] = self.request.GET.get("view", "queue" if context["is_principal"] and not context["current_status"] else "filtered")
        context["programs"] = Program.objects.filter(is_active=True).order_by("name")
        context["bulk_publish_form"] = BulkPublishForm()

        # Compute count metrics for navigation tabs
        if context["is_principal"]:
            base_qs = InternalMark.objects.all()
            context["pending_review_count"] = base_qs.filter(status=MarkStatus.SUBMITTED).count()
            context["approved_count"] = base_qs.filter(status=MarkStatus.APPROVED).count()
            context["published_count"] = base_qs.filter(status=MarkStatus.PUBLISHED).count()
            context["rejected_count"] = base_qs.filter(status=MarkStatus.REJECTED).count()
            context["draft_count"] = base_qs.filter(status=MarkStatus.DRAFT).count()
            context["total_count"] = base_qs.count()
        elif context["is_faculty"]:
            base_qs = InternalMark.objects.filter(entered_by=user)
            context["draft_count"] = base_qs.filter(status=MarkStatus.DRAFT).count()
            context["submitted_count"] = base_qs.filter(status=MarkStatus.SUBMITTED).count()
            context["approved_count"] = base_qs.filter(status=MarkStatus.APPROVED).count()
            context["rejected_count"] = base_qs.filter(status=MarkStatus.REJECTED).count()
            context["published_count"] = base_qs.filter(status=MarkStatus.PUBLISHED).count()
            context["total_count"] = base_qs.count()

        return context


class MarkCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Allows faculty to record internal assessment marks in Draft status.
    """

    model = InternalMark
    form_class = InternalMarkForm
    template_name = "internal_marks/form.html"
    success_url = reverse_lazy("internal_marks:list")
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role == UserRole.FACULTY

    def form_valid(self, form):
        form.instance.entered_by = self.request.user
        form.instance.status = MarkStatus.DRAFT
        messages.success(
            self.request,
            _(f"Internal mark draft saved for {form.instance.student.get_full_name() or form.instance.student.username} "
              f"({form.instance.subject}: {form.instance.marks_obtained}/{form.instance.max_marks})."),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _("Record Internal Assessment Mark")
        context["submit_button_text"] = _("Save Mark Draft")
        return context


class MarkUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows faculty to edit mark records they personally entered, strictly while
    in 'draft' or 'rejected' status. Prevents edits on submitted/approved/published marks.
    """

    model = InternalMark
    form_class = InternalMarkForm
    template_name = "internal_marks/form.html"
    success_url = reverse_lazy("internal_marks:list")
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role == UserRole.FACULTY

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InternalMark.objects.filter(status__in=[MarkStatus.DRAFT, MarkStatus.REJECTED])
        # Scoped to faculty creator + draft or rejected status only
        return InternalMark.objects.filter(
            entered_by=user,
            status__in=[MarkStatus.DRAFT, MarkStatus.REJECTED]
        )

    def form_valid(self, form):
        messages.success(
            self.request,
            _(f"Internal mark record for {form.instance.student.get_full_name() or form.instance.student.username} was updated."),
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = _(f"Edit Mark Entry: {self.object.subject}")
        context["submit_button_text"] = _("Save Revisions")
        context["is_edit"] = True
        context["review_comment"] = self.object.review_comment if self.object.status == MarkStatus.REJECTED else None
        return context


class MarkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows faculty to delete unsubmitted draft marks they created.
    """

    model = InternalMark
    template_name = "internal_marks/confirm_delete.html"
    success_url = reverse_lazy("internal_marks:list")
    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role == UserRole.FACULTY

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return InternalMark.objects.filter(status=MarkStatus.DRAFT)
        return InternalMark.objects.filter(entered_by=user, status=MarkStatus.DRAFT)

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Draft mark entry deleted successfully."),
        )
        return super().form_valid(form)


class MarkSubmitForReviewView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Faculty action: Submits a draft or rejected mark record to the Principal for formal review.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role == UserRole.FACULTY

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        user = request.user
        if user.is_superuser:
            mark = get_object_or_404(InternalMark, pk=pk, status__in=[MarkStatus.DRAFT, MarkStatus.REJECTED])
        else:
            mark = get_object_or_404(InternalMark, pk=pk, entered_by=user, status__in=[MarkStatus.DRAFT, MarkStatus.REJECTED])

        mark.status = MarkStatus.SUBMITTED
        # Reset previous rejection metadata on new submission
        mark.reviewed_by = None
        mark.reviewed_at = None
        mark.review_comment = ""
        mark.save()

        student_name = mark.student.get_full_name() or mark.student.username
        messages.success(
            request,
            _(f"Marks for {student_name} ({mark.subject}) submitted for Principal review and approval."),
        )
        return redirect("internal_marks:list")


class MarkReviewView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Principal / Super Admin evaluation view: Approve or Reject a submitted mark record.
    Rejection strictly requires a feedback commentary explaining corrections needed.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in [UserRole.PRINCIPAL, UserRole.SUPER_ADMIN]

    def get_mark(self, pk: int) -> InternalMark:
        return get_object_or_404(
            InternalMark.objects.select_related("student", "student__student_profile", "program", "entered_by"),
            pk=pk,
            status=MarkStatus.SUBMITTED,
        )

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        mark = self.get_mark(pk)
        form = MarkReviewForm()
        return render(
            request,
            "internal_marks/review.html",
            {
                "mark": mark,
                "form": form,
            },
        )

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        mark = self.get_mark(pk)
        form = MarkReviewForm(request.POST)

        if form.is_valid():
            action = form.cleaned_data["action"]
            comment = form.cleaned_data.get("review_comment", "").strip()

            mark.reviewed_by = request.user
            mark.reviewed_at = timezone.now()

            student_name = mark.student.get_full_name() or mark.student.username

            if action == MarkReviewForm.ACTION_APPROVE:
                mark.status = MarkStatus.APPROVED
                mark.review_comment = comment
                mark.save()
                messages.success(
                    request,
                    _(f"Marks for {student_name} ({mark.subject}: {mark.marks_obtained}/{mark.max_marks}) approved. Ready for publishing."),
                )
            elif action == MarkReviewForm.ACTION_REJECT:
                mark.status = MarkStatus.REJECTED
                mark.review_comment = comment
                mark.save()
                messages.warning(
                    request,
                    _(f"Marks for {student_name} ({mark.subject}) returned to {mark.entered_by.get_full_name() or mark.entered_by.username} for revision."),
                )

            return redirect("internal_marks:list")

        return render(
            request,
            "internal_marks/review.html",
            {
                "mark": mark,
                "form": form,
            },
        )


class MarkPublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Principal / Super Admin publishing action:
    Supports publishing individual approved records or bulk publishing all approved marks for a program.
    """

    login_url = reverse_lazy("accounts:login")

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in [UserRole.PRINCIPAL, UserRole.SUPER_ADMIN]

    def post(self, request: HttpRequest, pk: int = None) -> HttpResponse:
        now = timezone.now()

        # Individual publish
        if pk:
            mark = get_object_or_404(InternalMark, pk=pk, status=MarkStatus.APPROVED)
            mark.status = MarkStatus.PUBLISHED
            mark.published_at = now
            mark.save()

            student_name = mark.student.get_full_name() or mark.student.username
            messages.success(
                request,
                _(f"Internal mark record for {student_name} ({mark.subject}) is now officially published to the student portal."),
            )
            return redirect("internal_marks:list")

        # Bulk publish
        program_id = request.POST.get("program")
        queryset = InternalMark.objects.filter(status=MarkStatus.APPROVED)

        if program_id and program_id.isdigit():
            program = get_object_or_404(Program, pk=int(program_id))
            queryset = queryset.filter(program=program)
            prog_name = program.name
        else:
            prog_name = "All Academic Programs"

        updated_count = queryset.update(status=MarkStatus.PUBLISHED, published_at=now)

        if updated_count > 0:
            messages.success(
                request,
                _(f"Successfully published {updated_count} approved internal mark record(s) for {prog_name}."),
            )
        else:
            messages.info(
                request,
                _(f"No approved marks were awaiting publication for {prog_name}."),
            )

        return redirect("internal_marks:list")


class StudentMarksView(LoginRequiredMixin, ListView):
    """
    Student-only view: Displays student's own officially published internal assessment marks.
    Strictly isolated at queryset level so students NEVER see draft, submitted, or unpublished marks.
    """

    model = InternalMark
    template_name = "internal_marks/student_marks.html"
    context_object_name = "published_marks"
    login_url = reverse_lazy("accounts:login")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(self.login_url)

        # Allow student role or superadmin viewing
        if request.user.role != UserRole.STUDENT and not request.user.is_superuser:
            return HttpResponseForbidden("403 Forbidden: Only students can access the student scorecard.")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        # Strict isolation: Only published marks belonging to the logged-in student
        return InternalMark.objects.filter(
            student=user,
            status=MarkStatus.PUBLISHED
        ).select_related("program", "entered_by").order_by("program__name", "subject")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        marks = context["published_marks"]

        total_obtained = sum(m.marks_obtained for m in marks)
        total_max = sum(m.max_marks for m in marks)
        overall_percentage = round((total_obtained / total_max) * 100, 1) if total_max > 0 else 0.0

        context["total_obtained"] = total_obtained
        context["total_max"] = total_max
        context["overall_percentage"] = overall_percentage
        context["marks_count"] = len(marks)
        return context
