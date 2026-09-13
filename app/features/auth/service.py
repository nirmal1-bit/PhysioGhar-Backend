from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.core.security import create_access_token, hash_password, verify_password
from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, RegisterRequest


class RegistrationConflictError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InactiveAccountError(Exception):
    pass


class AuthService:
    def __init__(self, repository: AuthRepository | None = None) -> None:
        self.repository = repository or AuthRepository()

    async def register(self, request: RegisterRequest) -> dict[str, Any]:
        if len(request.password.encode("utf-8")) > 72:
            raise RegistrationConflictError("Password is too long")

        email = str(request.email).lower()
        username = request.username.lower()

        async with get_engine().begin() as connection:
            if await self.repository.find_by_email(connection, email):
                raise RegistrationConflictError("Email is already registered")
            if await self.repository.find_by_username(connection, username):
                raise RegistrationConflictError("Username is already taken")

            try:
                return await self.repository.create_therapist(
                    connection,
                    email=email,
                    name=request.name.strip(),
                    username=username,
                    password_hash=hash_password(request.password),
                )
            except IntegrityError as error:
                raise RegistrationConflictError(
                    "Email or username is already registered"
                ) from error

    async def login(self, request: LoginRequest) -> str:
        async with get_engine().connect() as connection:
            therapist = await self.repository.find_by_email(
                connection,
                str(request.email).lower(),
            )

        if not therapist or not verify_password(
            request.password,
            therapist["password_hash"],
        ):
            raise InvalidCredentialsError("Invalid email or password")
        if not therapist["is_active"]:
            raise InactiveAccountError("This account is inactive")

        return create_access_token(
            subject=str(therapist["id"]),
            user_type=therapist["user_type"],
        )
