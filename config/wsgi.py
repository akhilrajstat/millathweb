"""
config/wsgi.py
==============
WSGI entrypoint for Millath College ERP.
Used by gunicorn in production:
    gunicorn config.wsgi:application
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
