"""
apps/notices/apps.py
====================
AppConfig for announcements, circulars, and notices.
"""

from django.apps import AppConfig


class NoticesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notices"
    label = "notices"
    verbose_name = "Notices & Announcements"
