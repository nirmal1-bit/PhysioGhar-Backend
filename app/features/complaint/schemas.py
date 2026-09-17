from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

ComplaintCategory = Literal[
    "patient_issue",
    "booking_issue",
    "payment_issue",
    "technical_issue",
    "other",
]


class ComplaintRequest(BaseModel):
    category: ComplaintCategory
    subject: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=10000)


class ComplaintResponse(ComplaintRequest):
    id: int
    therapist_id: int
    status: str
    created_at: datetime
    updated_at: datetime
