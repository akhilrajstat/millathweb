"""
apps/gallery/views.py
=====================
Public photo gallery view displaying all campus images with optional category filtering.
"""

from collections import defaultdict
from django.views.generic import ListView
from .models import GalleryImage


class GalleryView(ListView):
    """
    Photo gallery grid view with category filters.
    """

    model = GalleryImage
    template_name = "gallery/gallery.html"
    context_object_name = "images"

    def get_queryset(self):
        queryset = GalleryImage.objects.all().order_by("display_order", "-upload_date")
        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category__iexact=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch distinct categories that are not empty
        categories = (
            GalleryImage.objects.exclude(category="")
            .values_list("category", flat=True)
            .distinct()
        )
        context["categories"] = sorted(list(set(categories)))
        context["selected_category"] = self.request.GET.get("category", "")
        return context
