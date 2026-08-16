"""
config/settings/development.py
===============================
Development-specific overrides.
Activate with:  DJANGO_SETTINGS_MODULE=config.settings.development
"""

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Email — print to the console so no real mail server is needed locally.
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Disable HTTPS-only redirects in local development.
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
