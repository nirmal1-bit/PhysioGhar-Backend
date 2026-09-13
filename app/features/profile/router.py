from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.security import get_current_therapist_id
from app.features.profile.schemas import ProfileRequest, ProfileResponse
from app.features.profile.service import (
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    ProfileService,
)

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    request: ProfileRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ProfileResponse | JSONResponse:
    try:
        profile = await ProfileService().create(therapist_id, request)
    except ProfileAlreadyExistsError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    return ProfileResponse.model_validate(profile)


@router.get("", response_model=ProfileResponse)
async def get_profile(
    therapist_id: int = Depends(get_current_therapist_id),
) -> ProfileResponse:
    try:
        profile = await ProfileService().get(therapist_id)
    except ProfileNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )
    return ProfileResponse.model_validate(profile)


@router.put("", response_model=ProfileResponse)
async def update_profile(
    request: ProfileRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ProfileResponse:
    try:
        profile = await ProfileService().update(therapist_id, request)
    except ProfileNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )
    return ProfileResponse.model_validate(profile)
