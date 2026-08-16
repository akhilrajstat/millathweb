"""
apps/faculty/urls.py
====================
URL patterns for faculty directory and profiles.
"""

from django.urls import path
from . import views

app_name = "faculty"

urlpatterns = [
    path("", views.FacultyListView.as_view(), name="list"),
    path("<int:pk>/", views.FacultyDetailView.as_view(), name="detail"),
]
