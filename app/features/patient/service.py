from typing import Any

from sqlalchemy.exc import IntegrityError

from app.core.database import get_engine
from app.features.patient.repository import PatientRepository
from app.features.patient.schemas import PatientNoteRequest, PatientRequest


class PatientNotFoundError(Exception):
    pass


class PatientAlreadyExistsError(Exception):
    pass


class PatientService:
    def __init__(self, repository: PatientRepository | None = None) -> None:
        self.repository = repository or PatientRepository()

    async def list(self, therapist_id: int) -> list[dict[str, Any]]:
        async with get_engine().connect() as connection:
            return await self.repository.list(connection, therapist_id)

    async def get_detail(
        self,
        therapist_id: int,
        patient_id: int,
    ) -> dict[str, Any]:
        async with get_engine().connect() as connection:
            patient = await self.repository.find(connection, therapist_id, patient_id)
            if not patient:
                raise PatientNotFoundError("Patient record not found")
            patient["sessions"] = await self.repository.sessions(
                connection, therapist_id, patient_id
            )
            patient["notes"] = await self.repository.notes(
                connection, therapist_id, patient_id
            )
            return patient

    async def create(
        self,
        therapist_id: int,
        request: PatientRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            try:
                return await self.repository.create(connection, therapist_id, request)
            except IntegrityError as error:
                raise PatientAlreadyExistsError(
                    "A patient with this email already exists"
                ) from error

    async def update(
        self,
        therapist_id: int,
        patient_id: int,
        request: PatientRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            patient = await self.repository.update(
                connection, therapist_id, patient_id, request
            )
        if not patient:
            raise PatientNotFoundError("Patient record not found")
        return patient

    async def delete(self, therapist_id: int, patient_id: int) -> None:
        async with get_engine().begin() as connection:
            deleted = await self.repository.delete(
                connection,
                therapist_id,
                patient_id,
            )
        if not deleted:
            raise PatientNotFoundError("Patient record not found")

    async def create_note(
        self,
        therapist_id: int,
        patient_id: int,
        request: PatientNoteRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            note = await self.repository.create_note(
                connection, therapist_id, patient_id, request
            )
        if not note:
            raise PatientNotFoundError(
                "Patient or linked booking was not found"
            )
        return note

    async def update_note(
        self,
        therapist_id: int,
        patient_id: int,
        note_id: int,
        request: PatientNoteRequest,
    ) -> dict[str, Any]:
        async with get_engine().begin() as connection:
            note = await self.repository.update_note(
                connection,
                therapist_id,
                patient_id,
                note_id,
                request,
            )
        if not note:
            raise PatientNotFoundError("Patient note not found")
        return note
