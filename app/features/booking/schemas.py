from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

BookingStatus = Literal["pending", "accepted", "completed", "declined", "cancelled"]
TherapistBookingStatus = Literal["accepted", "completed", "declined", "cancelled"]


class AvailableSlotResponse(BaseModel):
    id: int
    slot_date: date
    start_time: time
    end_time: time


class AvailableTherapistResponse(BaseModel):
    id: int
    name: str
    username: str
    profile_image_url: str | None
    experience_years: int | None
    specialization: str | None
    address: str | None
    slots: list[AvailableSlotResponse] = Field(default_factory=list)


class CreateBookingRequest(BaseModel):
    therapist_id: int = Field(gt=0)
    slot_id: int = Field(gt=0)
    patient_name: str = Field(min_length=2, max_length=120)
    patient_email: EmailStr
    patient_phone: str = Field(min_length=1, max_length=32)
    treatment: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=500)


class BookingResponse(BaseModel):
    id: int
    therapist_id: int
    slot_id: int
    patient_name: str
    patient_email: EmailStr
    patient_phone: str
    treatment: str
    location: str
    status: BookingStatus
    slot_date: date
    start_time: time
    end_time: time
    created_at: datetime
    updated_at: datetime


class BookingStatusRequest(BaseModel):
    status: TherapistBookingStatus
