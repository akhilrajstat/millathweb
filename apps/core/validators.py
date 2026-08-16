"""
apps/core/validators.py
=======================
Shared validator functions for model file fields and data validation.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB (5,242,880 bytes)


def validate_file_size_5mb(value):
    """
    Validate that an uploaded file does not exceed 5MB.
    Raises ValidationError with a descriptive error message if exceeded.
    """
    max_size = MAX_FILE_SIZE_BYTES
    if value and hasattr(value, "size") and value.size > max_size:
        size_mb = value.size / (1024 * 1024)
        raise ValidationError(
            _(f"File size cannot exceed 5MB. The uploaded file is {size_mb:.2f} MB."),
            code="file_too_large",
        )


def validate_image_extension(value):
    """
    Validate that the uploaded file has a valid image extension (jpg, jpeg, png, webp).
    """
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".webp"]
    if ext not in valid_extensions:
        raise ValidationError(
            _(f"Unsupported file extension '{ext}'. Allowed image formats are: JPG, JPEG, PNG, WEBP."),
            code="invalid_image_extension",
        )

