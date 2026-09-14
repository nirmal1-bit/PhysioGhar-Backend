from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.cloudinary_service import (
    CloudinaryConfigurationError,
    CloudinaryUploadError,
)
from app.core.security import get_current_therapist_id
from app.features.profile.schemas import ProfileRequest, ProfileResponse
from app.features.profile.service import (
    ProfileConflictError,
    ProfileNotFoundError,
    ProfileService,
)

router = APIRouter(prefix="/profile", tags=["profile"])

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024


async def _read_profile_image(image: UploadFile | None) -> tuple[bytes | None, str]:
    if image is None:
        return None, "profile-image"
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Profile image must be an image file",
        )

    content = await image.read()
    if len(content) > MAX_PROFILE_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Profile image must be smaller than 5 MB",
        )
    return content, image.filename or "profile-image"


async def profile_form(
    profile_image_url: Annotated[str | None, Form()] = None,
    phone: Annotated[str | None, Form()] = None,
    experience_years: Annotated[int, Form()] = 0,
    specialization: Annotated[str, Form()] = "",
    address: Annotated[str, Form()] = "",
) -> ProfileRequest:
    return ProfileRequest(
        profile_image_url=profile_image_url,
        phone=phone,
        experience_years=experience_years,
        specialization=specialization,
        address=address,
    )


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_profile(
    request: Annotated[ProfileRequest, Depends(profile_form)],
    image: Annotated[UploadFile | None, File()] = None,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ProfileResponse | JSONResponse:
    try:
        image_content, image_filename = await _read_profile_image(image)
        profile = await ProfileService().create(
            therapist_id,
            request,
            image_content,
            image_filename,
        )
    except ProfileConflictError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    except CloudinaryConfigurationError as error:
        return JSONResponse(status_code=503, content={"detail": str(error)})
    except CloudinaryUploadError as error:
        return JSONResponse(status_code=502, content={"detail": str(error)})
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
    request: Annotated[ProfileRequest, Depends(profile_form)],
    image: Annotated[UploadFile | None, File()] = None,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ProfileResponse:
    try:
        image_content, image_filename = await _read_profile_image(image)
        profile = await ProfileService().update(
            therapist_id,
            request,
            image_content,
            image_filename,
        )
    except ProfileConflictError as error:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error)},
        )
    except ProfileNotFoundError as error:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )
    except CloudinaryConfigurationError as error:
        return JSONResponse(status_code=503, content={"detail": str(error)})
    except CloudinaryUploadError as error:
        return JSONResponse(status_code=502, content={"detail": str(error)})
    return ProfileResponse.model_validate(profile)
