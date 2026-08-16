"""
apps/messaging/urls.py
======================
URL routing for in-app messaging and broadcast announcements.
"""

from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.InboxView.as_view(), name="inbox"),
    path("sent/", views.SentView.as_view(), name="sent"),
    path("compose/", views.ComposeView.as_view(), name="compose"),
    path("<int:pk>/", views.MessageDetailView.as_view(), name="detail"),
]
