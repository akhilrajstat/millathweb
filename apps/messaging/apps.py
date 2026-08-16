"""
apps/messaging/apps.py
======================
AppConfig for internal individual and broadcast messaging.
"""

from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.messaging"
    label = "messaging"
    verbose_name = "Internal Messaging & Broadcasts"
