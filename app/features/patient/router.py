from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.security import get_current_therapist_id
from app.features.patient.schemas import (
    PatientDetailResponse,
    PatientNoteRequest,
    PatientNoteResponse,
    PatientRequest,
    PatientResponse,
)
from app.features.patient.service import (
    PatientAlreadyExistsError,
    PatientNotFoundError,
    PatientService,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=list[PatientResponse])
async def list_patients(
    therapist_id: int = Depends(get_current_therapist_id),
) -> list[PatientResponse]:
    patients = await PatientService().list(therapist_id)
    return [PatientResponse.model_validate(patient) for patient in patients]


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: PatientRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> PatientResponse | JSONResponse:
    try:
        patient = await PatientService().create(therapist_id, request)
    except PatientAlreadyExistsError as error:
        return JSONResponse(status_code=409, content={"detail": str(error)})
    return PatientResponse.model_validate(patient)


@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(
    patient_id: int,
    therapist_id: int = Depends(get_current_therapist_id),
) -> PatientDetailResponse | JSONResponse:
    try:
        patient = await PatientService().get_detail(therapist_id, patient_id)
    except PatientNotFoundError as error:
        return JSONResponse(status_code=404, content={"detail": str(error)})
    return PatientDetailResponse.model_validate(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    request: PatientRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> PatientResponse | JSONResponse:
    try:
        patient = await PatientService().update(therapist_id, patient_id, request)
    except PatientNotFoundError as error:
        return JSONResponse(status_code=404, content={"detail": str(error)})
    return PatientResponse.model_validate(patient)


@router.delete("/{patient_id}", response_model=None)
async def delete_patient(
    patient_id: int,
    therapist_id: int = Depends(get_current_therapist_id),
) -> dict[str, str] | JSONResponse:
    try:
        await PatientService().delete(therapist_id, patient_id)
    except PatientNotFoundError as error:
        return JSONResponse(status_code=404, content={"detail": str(error)})
    return {"detail": "Patient deleted successfully"}


@router.post(
    "/{patient_id}/notes",
    response_model=PatientNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_patient_note(
    patient_id: int,
    request: PatientNoteRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> PatientNoteResponse | JSONResponse:
    try:
        note = await PatientService().create_note(therapist_id, patient_id, request)
    except PatientNotFoundError as error:
        return JSONResponse(status_code=404, content={"detail": str(error)})
    return PatientNoteResponse.model_validate(note)


@router.put("/{patient_id}/notes/{note_id}", response_model=PatientNoteResponse)
async def update_patient_note(
    patient_id: int,
    note_id: int,
    request: PatientNoteRequest,
    therapist_id: int = Depends(get_current_therapist_id),
) -> PatientNoteResponse | JSONResponse:
    try:
        note = await PatientService().update_note(
            therapist_id, patient_id, note_id, request
        )
    except PatientNotFoundError as error:
        return JSONResponse(status_code=404, content={"detail": str(error)})
    return PatientNoteResponse.model_validate(note)
