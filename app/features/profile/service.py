from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.features.profile.repository import ProfileRepository
from app.features.profile.schemas import ProfileRequest


class ProfileAlreadyExistsError(Exception):
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
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            try:
                return await self.repository.create(
                    connection,
                    therapist_id,
                    request,
                )
            except IntegrityError as error:
                raise ProfileAlreadyExistsError(
                    "A profile already exists for this therapist"
                ) from error

    async def update(
        self,
        therapist_id: int,
        request: ProfileRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            profile = await self.repository.update(
                connection,
                therapist_id,
                request,
            )
        if not profile:
            raise ProfileNotFoundError("Profile not found")
        return profile
