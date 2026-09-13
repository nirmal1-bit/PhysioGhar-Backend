from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection


class AuthRepository:
    async def find_by_email(
        self,
        connection: AsyncConnection,
        email: str,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                SELECT id, email, name, username, password_hash, user_type,
                       is_active, created_at
                FROM therapists
                WHERE LOWER(email) = LOWER(:email)
                """
            ),
            {"email": email},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def find_by_username(
        self,
        connection: AsyncConnection,
        username: str,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                SELECT id, email, name, username, password_hash, user_type,
                       is_active, created_at
                FROM therapists
                WHERE LOWER(username) = LOWER(:username)
                """
            ),
            {"username": username},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def create_therapist(
        self,
        connection: AsyncConnection,
        *,
        email: str,
        name: str,
        username: str,
        password_hash: str,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO therapists (email, name, username, password_hash)
                VALUES (:email, :name, :username, :password_hash)
                RETURNING id, email, name, username, user_type,
                          is_active, created_at
                """
            ),
            {
                "email": email,
                "name": name,
                "username": username,
                "password_hash": password_hash,
            },
        )
        return dict(result.mappings().one())
