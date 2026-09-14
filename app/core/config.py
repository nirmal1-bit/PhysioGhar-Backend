from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PhysioGhar API"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_url: str = (
        "postgresql+psycopg://postgres@localhost/physioghar?sslmode=disable"
    )
    jwt_secret_key: str = "change-this-development-secret"
    jwt_algorithm: str = "HS256"
    # Thirty days, expressed in minutes for the JWT expiry calculation.
    access_token_expire_minutes: int = 43_200
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None
    cloudinary_upload_folder: str = "physioghar/profiles"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
