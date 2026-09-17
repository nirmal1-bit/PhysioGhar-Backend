from datetime import date
from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.features.booking.repository import BookingRepository
from app.features.booking.schemas import (
    AvailableTherapistResponse,
    CreateBookingRequest,
)


class SlotUnavailableError(Exception):
    pass


class BookingNotFoundError(Exception):
    pass


class BookingService:
    def __init__(self, repository: BookingRepository | None = None) -> None:
        self.repository = repository or BookingRepository()

    async def list_available_therapists(
        self,
        selected_date: date,
    ) -> list[AvailableTherapistResponse]:
        async with get_engine().connect() as connection:
            rows = await self.repository.list_available_therapists(
                connection,
                selected_date,
            )

        therapists: dict[int, dict[str, Any]] = {}
        for row in rows:
            therapist = therapists.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "name": row["name"],
                    "username": row["username"],
                    "profile_image_url": row["profile_image_url"],
                    "experience_years": row["experience_years"],
                    "specialization": row["specialization"],
                    "address": row["address"],
                    "slots": [],
                },
            )
            therapist["slots"].append(
                {
                    "id": row["slot_id"],
                    "slot_date": row["slot_date"],
                    "start_time": row["start_time"],
                    "end_time": row["end_time"],
                }
            )
        return [
            AvailableTherapistResponse.model_validate(item)
            for item in therapists.values()
        ]

    async def list_available_slots(
        self,
        therapist_id: int,
        selected_date: date,
    ) -> list[dict[str, Any]]:
        async with get_engine().connect() as connection:
            return await self.repository.list_available_slots(
                connection,
                therapist_id,
                selected_date,
            )

    async def create_booking(self, request: CreateBookingRequest) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            try:
                booking = await self.repository.reserve_slot_and_create_booking(
                    connection,
                    request,
                )
            except IntegrityError as error:
                raise SlotUnavailableError("The slot is already requested") from error
        if not booking:
            raise SlotUnavailableError(
                "The slot is unavailable, blocked, already booked, "
                "or the therapist is unavailable"
            )
        return booking

    async def list_for_therapist(
        self,
        therapist_id: int,
        booking_status: str | None = None,
    ) -> list[dict[str, Any]]:
        async with get_engine().connect() as connection:
            return await self.repository.list_for_therapist(
                connection,
                therapist_id,
                booking_status,
            )

    async def update_status(
        self,
        therapist_id: int,
        booking_id: int,
        new_status: str,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            booking = await self.repository.update_status(
                connection,
                therapist_id,
                booking_id,
                new_status,
            )
            if not booking:
                raise BookingNotFoundError(
                    "Booking was not found or the status transition is invalid"
                )
        return booking

    async def reschedule(
        self,
        therapist_id: int,
        booking_id: int,
        new_slot_id: int,
        new_slot_date: date,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            booking = await self.repository.reschedule(
                connection,
                therapist_id,
                booking_id,
                new_slot_id,
                new_slot_date,
            )
            if not booking:
                raise BookingNotFoundError(
                    "Booking or target slot was not found, available, or valid"
                )
        return booking

    async def update_notes(
        self,
        therapist_id: int,
        booking_id: int,
        notes: str,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            booking = await self.repository.update_notes(
                connection,
                therapist_id,
                booking_id,
                notes,
            )
            if not booking:
                raise BookingNotFoundError(
                    "Booking was not found or does not accept therapist notes"
                )
        return booking
