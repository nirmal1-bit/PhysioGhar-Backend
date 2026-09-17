from datetime import date

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from app.core.security import get_current_therapist_id
from app.features.schedule.schemas import (
    AvailabilityRequest,
    AvailabilityResponse,
    CreateSlotRequest,
    ScheduleResponse,
    ScheduleSlotResponse,
    UpdateSlotStatusRequest,
)
from app.features.schedule.service import (
    ScheduleService,
    SlotAlreadyExistsError,
    SlotNotFoundError,
)

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/availability", response_model=AvailabilityResponse)
async def get_availability(
    therapist_id: int = Depends(get_current_therapist_id),
) -> AvailabilityResponse:
    availability = await ScheduleService().get_availability(therapist_id)
    return AvailabilityResponse.model_validate(availability)


@router.put("/availability", response_model=AvailabilityResponse)
async def update_availability(
    request: AvailabilityRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> AvailabilityResponse:
    availability = await ScheduleService().update_availability(
        therapist_id,
        request,
    )
    return AvailabilityResponse.model_validate(availability)


@router.get("", response_model=ScheduleResponse)
async def get_schedule(
    selected_date: date | None = Query(default=None, alias="date"),
    therapist_id: int = Depends(get_current_therapist_id),
) -> ScheduleResponse:
    schedule = await ScheduleService().get_week(therapist_id, selected_date)
    return ScheduleResponse.model_validate(schedule)


@router.post(
    "/slots",
    response_model=ScheduleSlotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_slot(
    request: CreateSlotRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ScheduleSlotResponse | JSONResponse:
    try:
        slot = await ScheduleService().create_slot(therapist_id, request)
    except SlotAlreadyExistsError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return ScheduleSlotResponse.model_validate(slot)


@router.patch("/slots/{slot_id}", response_model=ScheduleSlotResponse)
async def update_slot_status(
    slot_id: int,
    request: UpdateSlotStatusRequest,
    selected_date: date | None = Query(default=None, alias="date"),
    therapist_id: int = Depends(get_current_therapist_id),
) -> ScheduleSlotResponse | JSONResponse:
    try:
        slot = await ScheduleService().update_slot_status(
            therapist_id,
            slot_id,
            request.status,
            selected_date or date.today(),
        )
    except SlotNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )
    return ScheduleSlotResponse.model_validate(slot)
