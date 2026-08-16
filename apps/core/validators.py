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


def validate_image_file(value):
    """
    Validate that an uploaded file is a genuine, non-corrupted image file (JPG, PNG, WEBP)
    and does not exceed 5MB. Provides clear, friendly error messages for non-technical users.
    """
    from PIL import Image

    if not value:
        return

    # Check file size first
    validate_file_size_5mb(value)

    # Check extension
    validate_image_extension(value)

    # Verify actual image content using Pillow
    try:
        if hasattr(value, "file"):
            # Django UploadedFile or FieldFile
            image = Image.open(value.file)
            image.verify()
            if hasattr(value.file, "seek"):
                value.file.seek(0)
        elif hasattr(value, "open"):
            with value.open("rb") as f:
                image = Image.open(f)
                image.verify()
        else:
            image = Image.open(value)
            image.verify()
            if hasattr(value, "seek"):
                value.seek(0)
    except ValidationError:
        raise
    except Exception:
        raise ValidationError(
            _(
                "The uploaded file could not be recognized as a valid image. "
                "Please make sure you are uploading a genuine image file (JPG, PNG, or WEBP) and that it is not corrupted."
            ),
            code="invalid_image_content",
        )

