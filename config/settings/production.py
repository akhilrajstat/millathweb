"""
config/settings/production.py
==============================
Production-specific overrides — all security flags are ACTIVE (not commented out).
Activate with:  DJANGO_SETTINGS_MODULE=config.settings.production
"""

from .base import *  # noqa: F401, F403
from .base import env

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

# ---------------------------------------------------------------------------
# HTTPS / SSL enforcement
# ---------------------------------------------------------------------------
SECURE_SSL_REDIRECT = True

# ---------------------------------------------------------------------------
# Cookie security
# ---------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ---------------------------------------------------------------------------
# HTTP Strict Transport Security (HSTS)
# ---------------------------------------------------------------------------
SECURE_HSTS_SECONDS = 31_536_000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ---------------------------------------------------------------------------
# Email — configured entirely via environment variables
# ---------------------------------------------------------------------------
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    default="Millath College ERP <noreply@example.com>",
)

# ---------------------------------------------------------------------------
# Additional production security hardening
# ---------------------------------------------------------------------------
# Prevent clickjacking — redundant with base.py's X_FRAME_OPTIONS = "DENY"
# but explicit for clarity in production review.
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
