from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.core.security import get_current_therapist_id
from app.features.booking.schemas import (
    AvailableSlotResponse,
    AvailableTherapistResponse,
    BookingNotesRequest,
    BookingResponse,
    BookingStatusRequest,
    CreateBookingRequest,
    RescheduleBookingRequest,
)
from app.features.booking.service import (
    BookingNotFoundError,
    BookingService,
    SlotUnavailableError,
)

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get(
    "/available-therapists",
    response_model=list[AvailableTherapistResponse],
)
async def list_available_therapists(
    selected_date: date | None = Query(default=None, alias="date"),
) -> list[AvailableTherapistResponse]:
    return await BookingService().list_available_therapists(
        selected_date or date.today(),
    )


@router.get(
    "/therapists/{therapist_id}/available-slots",
    response_model=list[AvailableSlotResponse],
)
async def list_available_slots(
    therapist_id: int,
    selected_date: date | None = Query(default=None, alias="date"),
) -> list[AvailableSlotResponse]:
    slots = await BookingService().list_available_slots(
        therapist_id,
        selected_date or date.today(),
    )
    return [AvailableSlotResponse.model_validate(slot) for slot in slots]


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_booking(
    request: CreateBookingRequest,
) -> BookingResponse | JSONResponse:
    try:
        booking = await BookingService().create_booking(request)
    except SlotUnavailableError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return BookingResponse.model_validate(booking)


@router.get("/therapist", response_model=list[BookingResponse])
async def list_therapist_bookings(
    booking_status: str | None = Query(default=None, alias="status"),
    therapist_id: int = Depends(get_current_therapist_id),
) -> list[BookingResponse]:
    bookings = await BookingService().list_for_therapist(
        therapist_id,
        booking_status,
    )
    return [BookingResponse.model_validate(booking) for booking in bookings]


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: int,
    request: BookingStatusRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> BookingResponse | JSONResponse:
    try:
        booking = await BookingService().update_status(
            therapist_id,
            booking_id,
            request.status,
        )
    except BookingNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return BookingResponse.model_validate(booking)


@router.patch("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: int,
    request: RescheduleBookingRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> BookingResponse | JSONResponse:
    try:
        booking = await BookingService().reschedule(
            therapist_id,
            booking_id,
            request.slot_id,
            request.slot_date,
        )
    except BookingNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return BookingResponse.model_validate(booking)


@router.patch("/{booking_id}/notes", response_model=BookingResponse)
async def update_booking_notes(
    booking_id: int,
    request: BookingNotesRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> BookingResponse | JSONResponse:
    try:
        booking = await BookingService().update_notes(
            therapist_id,
            booking_id,
            request.notes,
        )
    except BookingNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return BookingResponse.model_validate(booking)
