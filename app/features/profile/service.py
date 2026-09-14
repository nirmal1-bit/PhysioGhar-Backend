import asyncio
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.cloudinary_service import upload_profile_image
from app.core.database import get_engine
from app.features.profile.repository import ProfileRepository
from app.features.profile.schemas import ProfileRequest


class ProfileConflictError(Exception):
    pass


class ProfileNotFoundError(Exception):
    pass


class ProfileService:
    def __init__(self, repository: ProfileRepository | None = None) -> None:
        self.repository = repository or ProfileRepository()

    async def get(self, therapist_id: int) -> dict[str, Any]:
        async with get_engine().connect() as connection:
            profile = await self.repository.find_by_therapist_id(
                connection,
                therapist_id,
            )
        if not profile:
            raise ProfileNotFoundError("Profile not found")
        return profile

    async def create(
        self,
        therapist_id: int,
        request: ProfileRequest,
        image_content: bytes | None = None,
        image_filename: str = "profile-image",
    ) -> dict[str, Any]:
        request = await self._with_uploaded_image(
            request,
            image_content=image_content,
            image_filename=image_filename,
        )
        async with get_engine().begin() as connection:
            try:
                return await self.repository.create(
                    connection,
                    therapist_id,
                    request,
                )
            except IntegrityError as error:
                message = "A profile already exists for this therapist"
                if "therapists_email_lower_unique" in str(error.orig):
                    message = "That email is already in use"
                raise ProfileConflictError(message) from error

    async def update(
        self,
        therapist_id: int,
        request: ProfileRequest,
        image_content: bytes | None = None,
        image_filename: str = "profile-image",
    ) -> dict[str, Any]:
        request = await self._with_uploaded_image(
            request,
            image_content=image_content,
            image_filename=image_filename,
        )
        async with get_engine().begin() as connection:
            try:
                profile = await self.repository.update(
                    connection,
                    therapist_id,
                    request,
                )
            except IntegrityError as error:
                if "therapists_email_lower_unique" in str(error.orig):
                    raise ProfileConflictError(
                        "That email is already in use"
                    ) from error
                raise
        if not profile:
            raise ProfileNotFoundError("Profile not found")
        return profile

    async def _with_uploaded_image(
        self,
        request: ProfileRequest,
        *,
        image_content: bytes | None,
        image_filename: str,
    ) -> ProfileRequest:
        if image_content is None:
            return request

        image_url = await asyncio.to_thread(
            upload_profile_image,
            content=image_content,
            filename=image_filename,
        )
        return request.model_copy(update={"profile_image_url": image_url})
