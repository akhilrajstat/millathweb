"""
apps/core/apps.py
=================
AppConfig for the core site-wide application.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"
    verbose_name = "Core & Site Settings"
