"""
config/urls.py
==============
Root URL configuration for Millath College ERP & Public Website.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # CKEditor 5 upload and browser URLs
    path("ckeditor5/", include("django_ckeditor_5.urls")),

    # Accounts & ERP authentication
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # Public website apps
    path("programs/", include("apps.programs.urls", namespace="programs")),
    path("faculty/", include("apps.faculty.urls", namespace="faculty")),
    path("notices/", include("apps.notices.urls", namespace="notices")),
    path("gallery/", include("apps.gallery.urls", namespace="gallery")),

    # ERP Messaging module
    path("messages/", include("apps.messaging.urls", namespace="messaging")),

    # ERP Assignments module
    path("assignments/", include("apps.assignments.urls", namespace="assignments")),

    # ERP Internal Assessment Marks module
    path("internal-marks/", include("apps.internal_marks.urls", namespace="internal_marks")),

    # Core app (Homepage, About, Contact) at the root
    path("", include("apps.core.urls", namespace="core")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
