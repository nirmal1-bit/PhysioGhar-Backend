from typing import Any

from app.core.database import get_engine
from app.features.complaint.repository import ComplaintRepository
from app.features.complaint.schemas import ComplaintRequest


class ComplaintService:
    def __init__(self, repository: ComplaintRepository | None = None) -> None:
        self.repository = repository or ComplaintRepository()

    async def list(self, therapist_id: int) -> list[dict[str, Any]]:
        async with get_engine().connect() as connection:
            return await self.repository.list(connection, therapist_id)

    async def create(
        self,
        therapist_id: int,
        request: ComplaintRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            return await self.repository.create(connection, therapist_id, request)
