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
    slot_date: date
    patient_name: str = Field(min_length=2, max_length=120)
    patient_email: EmailStr
    patient_phone: str = Field(min_length=1, max_length=32)
    patient_age: int | None = Field(default=None, ge=0, le=150)
    patient_gender: str | None = Field(default=None, max_length=32)
    patient_condition: str | None = Field(default=None, max_length=255)
    treatment: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=500)


class BookingResponse(BaseModel):
    id: int
    therapist_id: int
    patient_id: int | None
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
    therapist_notes: str | None
    created_at: datetime
    updated_at: datetime


class BookingStatusRequest(BaseModel):
    status: TherapistBookingStatus


class RescheduleBookingRequest(BaseModel):
    slot_id: int = Field(gt=0)
    slot_date: date


class BookingNotesRequest(BaseModel):
    notes: str = Field(max_length=5000)
