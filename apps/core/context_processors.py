"""
apps/core/context_processors.py
===============================
Context processors for injecting global site settings into every template.
"""

from typing import Dict, Any
from django.http import HttpRequest
from .models import SiteSettings


def site_settings(request: HttpRequest) -> Dict[str, Any]:
    """
    Injects `site_settings` into every template context.
    """
    return {
        "site_settings": SiteSettings.get_solo(),
    }
