from __future__ import annotations

from io import BytesIO

import cloudinary
import cloudinary.uploader

from app.core.config import get_settings


class CloudinaryConfigurationError(Exception):
    pass


class CloudinaryUploadError(Exception):
    pass


def upload_profile_image(*, content: bytes, filename: str) -> str:
    settings = get_settings()
    if not all(
        (
            settings.cloudinary_cloud_name,
            settings.cloudinary_api_key,
            settings.cloudinary_api_secret,
        )
    ):
        raise CloudinaryConfigurationError("Cloudinary upload is not configured")

    cloudinary.config(
        cloud_name=settings.cloudinary_cloud_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    try:
        result = cloudinary.uploader.upload(
            BytesIO(content),
            folder=settings.cloudinary_upload_folder,
            resource_type="image",
            use_filename=True,
            unique_filename=True,
            filename_override=filename,
        )
    except Exception as error:
        raise CloudinaryUploadError("Could not upload profile image") from error

    secure_url = result.get("secure_url")
    if not secure_url:
        raise CloudinaryUploadError("Cloudinary returned no secure image URL")
    return secure_url
