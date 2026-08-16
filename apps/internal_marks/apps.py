from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InternalMarksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.internal_marks"
    verbose_name = _("Internal Assessment Marks")
