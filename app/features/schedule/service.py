from datetime import date, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.features.schedule.repository import ScheduleRepository
from app.features.schedule.schemas import (
    AvailabilityRequest,
    CreateSlotRequest,
    EditableSlotStatus,
)


class SlotAlreadyExistsError(Exception):
    pass


class SlotNotFoundError(Exception):
    pass


class ScheduleService:
    def __init__(self, repository: ScheduleRepository | None = None) -> None:
        self.repository = repository or ScheduleRepository()

    async def get_availability(self, therapist_id: int) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            return await self.repository.get_availability(connection, therapist_id)

    async def update_availability(
        self,
        therapist_id: int,
        request: AvailabilityRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            return await self.repository.update_availability(
                connection,
                therapist_id,
                request,
            )

    async def get_week(
        self,
        therapist_id: int,
        selected_date: date | None,
    ) -> dict[str, Any]:
        current_date = selected_date or date.today()
        week_start = current_date - timedelta(days=current_date.weekday())
        week_end = week_start + timedelta(days=6)

        async with get_engine().connect() as connection:
            slots = await self.repository.list_slots(
                connection,
                therapist_id,
                week_start,
                week_end,
            )
        return {
            "week_start": week_start,
            "week_end": week_end,
            "slots": slots,
        }

    async def create_slot(
        self,
        therapist_id: int,
        request: CreateSlotRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            try:
                return await self.repository.create_slot(
                    connection,
                    therapist_id,
                    request,
                )
            except IntegrityError as error:
                raise SlotAlreadyExistsError(
                    "A slot with the same time already exists"
                ) from error

    async def update_slot_status(
        self,
        therapist_id: int,
        slot_id: int,
        status: EditableSlotStatus,
        selected_date: date,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            slot = await self.repository.update_slot_status(
                connection,
                therapist_id,
                slot_id,
                status,
                selected_date,
            )
        if not slot:
            raise SlotNotFoundError("Schedule slot not found")
        return slot
