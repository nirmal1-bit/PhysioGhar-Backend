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
                SELECT p.id, p.therapist_id, t.name, t.email,
                       p.profile_image_url, p.phone, p.experience_years,
                       p.specialization, p.address, p.created_at, p.updated_at
                FROM profiles p
                JOIN therapists t ON t.id = p.therapist_id
                WHERE p.therapist_id = :therapist_id
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
        profile = dict(result.mappings().one())
        return await self._with_therapist(connection, profile, therapist_id)

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
                SET profile_image_url = COALESCE(
                        :profile_image_url, profile_image_url
                    ),
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
        if not row:
            return None
        return await self._with_therapist(
            connection,
            dict(row),
            therapist_id,
        )

    async def _with_therapist(
        self,
        connection: AsyncConnection,
        profile: dict[str, Any],
        therapist_id: int,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                SELECT name, email
                FROM therapists
                WHERE id = :therapist_id
                """
            ),
            {"therapist_id": therapist_id},
        )
        therapist = result.mappings().one()
        return {**profile, "name": therapist["name"], "email": therapist["email"]}
