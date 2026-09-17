from datetime import date, datetime, time

from pydantic import BaseModel, EmailStr, Field


class PatientRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: str | None = Field(default=None, max_length=32)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=32)
    condition: str = Field(min_length=1, max_length=255)


class PatientResponse(PatientRequest):
    id: int
    therapist_id: int
    last_session_date: date | None = None
    created_at: datetime
    updated_at: datetime


class PatientSessionResponse(BaseModel):
    booking_id: int
    treatment: str
    location: str
    status: str
    slot_date: date
    start_time: time
    end_time: time


class PatientNoteRequest(BaseModel):
    note: str = Field(min_length=1, max_length=10000)
    exercises: str | None = Field(default=None, max_length=10000)
    next_session: str | None = Field(default=None, max_length=2000)
    booking_id: int = Field(gt=0)


class PatientNoteResponse(PatientNoteRequest):
    id: int
    patient_id: int
    created_at: datetime
    updated_at: datetime


class PatientDetailResponse(PatientResponse):
    sessions: list[PatientSessionResponse] = Field(default_factory=list)
    notes: list[PatientNoteResponse] = Field(default_factory=list)
