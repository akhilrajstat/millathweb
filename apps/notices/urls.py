"""
apps/notices/urls.py
====================
URL routes for notices and announcements.
"""

from django.urls import path
from . import views

app_name = "notices"

urlpatterns = [
    path("", views.NoticeListView.as_view(), name="list"),
    path("<slug:slug>/", views.NoticeDetailView.as_view(), name="detail"),
]
