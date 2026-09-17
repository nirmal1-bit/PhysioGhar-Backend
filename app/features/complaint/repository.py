from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.features.complaint.schemas import ComplaintRequest


class ComplaintRepository:
    async def list(
        self,
        connection: AsyncConnection,
        therapist_id: int,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT id, therapist_id, category, subject, description,
                       status, created_at, updated_at
                FROM complaints
                WHERE therapist_id = :therapist_id
                ORDER BY created_at DESC
                """
            ),
            {"therapist_id": therapist_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def create(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: ComplaintRequest,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO complaints (therapist_id, category, subject, description)
                VALUES (:therapist_id, :category, :subject, :description)
                RETURNING id, therapist_id, category, subject, description,
                          status, created_at, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump()},
        )
        return dict(result.mappings().one())
