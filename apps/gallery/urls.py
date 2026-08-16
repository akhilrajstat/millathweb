"""
apps/gallery/urls.py
====================
URL routes for the photo gallery.
"""

from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path("", views.GalleryView.as_view(), name="gallery"),
]
