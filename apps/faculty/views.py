"""
apps/faculty/views.py
=====================
Public views displaying faculty profiles and individual bios.
"""

from django.views.generic import ListView, DetailView
from .models import FacultyProfile


class FacultyListView(ListView):
    """
    Public directory of verified and published faculty members.
    """

    model = FacultyProfile
    template_name = "faculty/list.html"
    context_object_name = "faculty_list"

    def get_queryset(self):
        return (
            FacultyProfile.objects.filter(is_published=True)
            .select_related("user")
            .order_by("display_order", "user__first_name", "user__last_name")
        )


class FacultyDetailView(DetailView):
    """
    Public biographical profile for a single faculty member.
    """

    model = FacultyProfile
    template_name = "faculty/detail.html"
    context_object_name = "faculty_member"

    def get_queryset(self):
        return FacultyProfile.objects.filter(is_published=True).select_related("user")
