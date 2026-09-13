from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.features.schedule.schemas import (
    AvailabilityRequest,
    CreateSlotRequest,
    EditableSlotStatus,
)


class ScheduleRepository:
    async def get_availability(
        self,
        connection: AsyncConnection,
        therapist_id: int,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO therapist_availability (therapist_id)
                VALUES (:therapist_id)
                ON CONFLICT (therapist_id) DO NOTHING
                RETURNING is_available, updated_at
                """
            ),
            {"therapist_id": therapist_id},
        )
        row = result.mappings().first()
        if row:
            return dict(row)

        result = await connection.execute(
            text(
                """
                SELECT is_available, updated_at
                FROM therapist_availability
                WHERE therapist_id = :therapist_id
                """
            ),
            {"therapist_id": therapist_id},
        )
        return dict(result.mappings().one())

    async def update_availability(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: AvailabilityRequest,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO therapist_availability (
                    therapist_id, is_available
                )
                VALUES (:therapist_id, :is_available)
                ON CONFLICT (therapist_id) DO UPDATE
                SET is_available = EXCLUDED.is_available,
                    updated_at = NOW()
                RETURNING is_available, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump()},
        )
        return dict(result.mappings().one())

    async def list_slots(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        week_start: date,
        week_end: date,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT id, slot_date, start_time, end_time, status,
                       created_at, updated_at
                FROM schedule_slots
                WHERE therapist_id = :therapist_id
                  AND slot_date BETWEEN :week_start AND :week_end
                ORDER BY slot_date, start_time
                """
            ),
            {
                "therapist_id": therapist_id,
                "week_start": week_start,
                "week_end": week_end,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def create_slot(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: CreateSlotRequest,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO schedule_slots (
                    therapist_id, slot_date, start_time, end_time
                )
                VALUES (
                    :therapist_id, :slot_date, :start_time, :end_time
                )
                RETURNING id, slot_date, start_time, end_time, status,
                          created_at, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump()},
        )
        return dict(result.mappings().one())

    async def update_slot_status(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        slot_id: int,
        status: EditableSlotStatus,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                UPDATE schedule_slots
                SET status = :status, updated_at = NOW()
                WHERE id = :slot_id
                  AND therapist_id = :therapist_id
                RETURNING id, slot_date, start_time, end_time, status,
                          created_at, updated_at
                """
            ),
            {
                "therapist_id": therapist_id,
                "slot_id": slot_id,
                "status": status,
            },
        )
        row = result.mappings().first()
        return dict(row) if row else None
