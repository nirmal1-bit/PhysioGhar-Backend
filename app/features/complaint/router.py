from fastapi import APIRouter, Depends, status

from app.core.security import get_current_therapist_id
from app.features.complaint.schemas import ComplaintRequest, ComplaintResponse
from app.features.complaint.service import ComplaintService

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.get("", response_model=list[ComplaintResponse])
async def list_complaints(
    therapist_id: int = Depends(get_current_therapist_id),
) -> list[ComplaintResponse]:
    complaints = await ComplaintService().list(therapist_id)
    return [ComplaintResponse.model_validate(complaint) for complaint in complaints]


@router.post(
    "",
    response_model=ComplaintResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_complaint(
    request: ComplaintRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> ComplaintResponse:
    complaint = await ComplaintService().create(therapist_id, request)
    return ComplaintResponse.model_validate(complaint)
