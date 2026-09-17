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
                FROM users
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
                FROM users
                WHERE LOWER(username) = LOWER(:username)
                """
            ),
            {"username": username},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def create_user(
        self,
        connection: AsyncConnection,
        *,
        email: str,
        name: str,
        username: str,
        password_hash: str,
        user_type: str,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO users (
                    email, name, username, password_hash, user_type
                )
                VALUES (
                    :email, :name, :username, :password_hash, :user_type
                )
                RETURNING id, email, name, username, user_type,
                          is_active, created_at
                """
            ),
            {
                "email": email,
                "name": name,
                "username": username,
                "password_hash": password_hash,
                "user_type": user_type,
            },
        )
        return dict(result.mappings().one())
