"""
config/settings/production.py
==============================
Production-specific overrides for Render deployment.
All security flags are ACTIVE.
Activate with: DJANGO_SETTINGS_MODULE=config.settings.production
"""

import dj_database_url
from .base import *  # noqa: F401, F403
from .base import BASE_DIR, env

# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------
DEBUG = False

# Render and custom domains
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[]) + [".onrender.com"]

# CSRF Trusted Origins for Render subdomains and custom domains
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://*.onrender.com"],
)
if "https://*.onrender.com" not in CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS.append("https://*.onrender.com")

# ---------------------------------------------------------------------------
# Database — Render PostgreSQL via DATABASE_URL
# ---------------------------------------------------------------------------
DATABASE_URL = env("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# ---------------------------------------------------------------------------
# HTTPS / SSL enforcement & Proxy headers
# ---------------------------------------------------------------------------
# Render terminates SSL at load balancer and passes X-Forwarded-Proto header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True

# ---------------------------------------------------------------------------
# Cookie security
# ---------------------------------------------------------------------------
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# ---------------------------------------------------------------------------
# HTTP Strict Transport Security (HSTS)
# ---------------------------------------------------------------------------
SECURE_HSTS_SECONDS = 31_536_000  # 1 year
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
    default="Millath College ERP <noreply@millathcollege.edu.in>",
)

# ---------------------------------------------------------------------------
# Additional production security hardening
# ---------------------------------------------------------------------------
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
