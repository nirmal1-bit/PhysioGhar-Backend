from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, model_validator

SlotStatus = Literal["open", "booked", "blocked"]
EditableSlotStatus = Literal["open", "blocked"]


class AvailabilityResponse(BaseModel):
    is_available: bool
    updated_at: datetime


class AvailabilityRequest(BaseModel):
    is_available: bool


class CreateSlotRequest(BaseModel):
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time

    @model_validator(mode="after")
    def validate_time_range(self) -> "CreateSlotRequest":
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time")
        return self


class UpdateSlotStatusRequest(BaseModel):
    status: EditableSlotStatus


class ScheduleSlotResponse(BaseModel):
    id: int
    slot_date: date
    day_of_week: int
    start_time: time
    end_time: time
    status: SlotStatus
    created_at: datetime
    updated_at: datetime


class ScheduleResponse(BaseModel):
    week_start: date
    week_end: date
    slots: list[ScheduleSlotResponse] = Field(default_factory=list)
