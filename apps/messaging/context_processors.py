"""
apps/messaging/context_processors.py
====================================
Context processor providing unread message counts for authenticated users.
"""

from typing import Dict, Any
from django.http import HttpRequest
from .models import Message


def unread_messages(request: HttpRequest) -> Dict[str, Any]:
    """
    Returns unread direct message count for the current authenticated user.
    """
    if request.user.is_authenticated:
        count = Message.objects.filter(recipient=request.user, is_read=False).count()
        return {"unread_messages_count": count}
    return {"unread_messages_count": 0}
