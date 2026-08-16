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

# ---------------------------------------------------------------------------
# django-debug-toolbar (optional; install separately if needed)
# ---------------------------------------------------------------------------
# Uncomment when django-debug-toolbar is added to requirements.txt:
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
# INTERNAL_IPS = ["127.0.0.1"]
