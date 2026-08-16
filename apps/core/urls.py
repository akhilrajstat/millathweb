"""
apps/core/urls.py
=================
URL patterns for the core app (Homepage, About, Contact).
"""

from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("coming-soon/", views.ComingSoonView.as_view(), name="coming_soon_default"),
    path("coming-soon/<str:feature>/", views.ComingSoonView.as_view(), name="coming_soon"),
]
