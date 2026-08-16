"""
apps/internal_marks/urls.py
===========================
URL routing configuration for internal assessment marks, principal reviews, and student grades.
"""

from django.urls import path
from apps.internal_marks import views

app_name = "internal_marks"

urlpatterns = [
    path("", views.MarkEntryListView.as_view(), name="list"),
    path("create/", views.MarkCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", views.MarkUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.MarkDeleteView.as_view(), name="delete"),
    path("<int:pk>/submit-for-review/", views.MarkSubmitForReviewView.as_view(), name="submit_for_review"),
    path("<int:pk>/review/", views.MarkReviewView.as_view(), name="review"),
    path("publish/", views.MarkPublishView.as_view(), name="bulk_publish"),
    path("<int:pk>/publish/", views.MarkPublishView.as_view(), name="publish"),
    path("my-scores/", views.StudentMarksView.as_view(), name="student_marks"),
]
