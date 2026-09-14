from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class ProfileRequest(BaseModel):
    profile_image_url: str | None = Field(default=None, max_length=2048)
    phone: str | None = Field(default=None, max_length=32)
    experience_years: int = Field(ge=0)
    specialization: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)


class ProfileResponse(ProfileRequest):
    id: int
    therapist_id: int
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
