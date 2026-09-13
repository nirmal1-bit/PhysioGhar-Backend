from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.features.profile.schemas import ProfileRequest


class ProfileRepository:
    async def find_by_therapist_id(
        self,
        connection: AsyncConnection,
        therapist_id: int,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                SELECT id, therapist_id, profile_image_url, phone,
                       experience_years, specialization, address,
                       created_at, updated_at
                FROM profiles
                WHERE therapist_id = :therapist_id
                """
            ),
            {"therapist_id": therapist_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def create(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: ProfileRequest,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO profiles (
                    therapist_id, profile_image_url, phone,
                    experience_years, specialization, address
                )
                VALUES (
                    :therapist_id, :profile_image_url, :phone,
                    :experience_years, :specialization, :address
                )
                RETURNING id, therapist_id, profile_image_url, phone,
                          experience_years, specialization, address,
                          created_at, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump()},
        )
        return dict(result.mappings().one())

    async def update(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: ProfileRequest,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                UPDATE profiles
                SET profile_image_url = :profile_image_url,
                    phone = :phone,
                    experience_years = :experience_years,
                    specialization = :specialization,
                    address = :address,
                    updated_at = NOW()
                WHERE therapist_id = :therapist_id
                RETURNING id, therapist_id, profile_image_url, phone,
                          experience_years, specialization, address,
                          created_at, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump()},
        )
        row = result.mappings().first()
        return dict(row) if row else None
