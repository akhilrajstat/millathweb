"""
apps/assignments/urls.py
========================
URL routing definitions for assignments, submissions, and grading.
"""

from django.urls import path
from apps.assignments import views

app_name = "assignments"

urlpatterns = [
    path("", views.AssignmentListView.as_view(), name="list"),
    path("create/", views.AssignmentCreateView.as_view(), name="create"),
    path("<int:pk>/", views.AssignmentDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.AssignmentUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.AssignmentDeleteView.as_view(), name="delete"),
    path("<int:assignment_id>/submit/", views.SubmissionSubmitView.as_view(), name="submit"),
    path("submissions/<int:pk>/grade/", views.GradeSubmissionView.as_view(), name="grade"),
]
