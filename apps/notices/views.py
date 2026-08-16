"""
apps/notices/views.py
=====================
Public views for browsing announcements, circulars, and reading notice details.
"""

from django.views.generic import ListView, DetailView
from .models import Notice, NoticeCategory


class NoticeListView(ListView):
    """
    List of active notices and circulars, ordered chronologically with category filtering.
    """

    model = Notice
    template_name = "notices/list.html"
    context_object_name = "notices"
    paginate_by = 10

    def get_queryset(self):
        queryset = Notice.objects.filter(is_active=True).order_by("-publish_date", "-id")
        category = self.request.GET.get("category")
        if category and category in NoticeCategory.values:
            queryset = queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = NoticeCategory.choices
        context["selected_category"] = self.request.GET.get("category", "")
        return context


class NoticeDetailView(DetailView):
    """
    Detail page for reading a full circular and downloading any attached document.
    """

    model = Notice
    template_name = "notices/detail.html"
    context_object_name = "notice"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Notice.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recent_notices"] = (
            Notice.objects.filter(is_active=True)
            .exclude(pk=self.object.pk)
            .order_by("-publish_date", "-id")[:5]
        )
        return context
