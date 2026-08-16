"""
apps/programs/views.py
======================
Public views for browsing academic programs and viewing detailed course curriculum.
"""

from django.views.generic import ListView, DetailView
from .models import Program


class ProgramListView(ListView):
    """
    List of active academic programs offered by the institution.
    """

    model = Program
    template_name = "programs/list.html"
    context_object_name = "programs"

    def get_queryset(self):
        return Program.objects.filter(is_active=True).order_by("name")


class ProgramDetailView(DetailView):
    """
    Detail page for a specific academic program identified by its slug.
    """

    model = Program
    template_name = "programs/detail.html"
    context_object_name = "program"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Program.objects.filter(is_active=True)
