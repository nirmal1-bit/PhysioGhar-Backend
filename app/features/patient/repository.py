from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.features.patient.schemas import PatientNoteRequest, PatientRequest


class PatientRepository:
    async def list(
        self,
        connection: AsyncConnection,
        therapist_id: int,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT p.id, p.therapist_id, p.name, p.age, p.gender,
                       p.email, p.phone, p.condition,
                       MAX(b.appointment_date) FILTER (WHERE b.status = 'completed')
                           AS last_session_date,
                       p.created_at, p.updated_at
                FROM patients p
                LEFT JOIN bookings b ON b.patient_id = p.id
                LEFT JOIN schedule_slots s ON s.id = b.slot_id
                WHERE p.therapist_id = :therapist_id
                GROUP BY p.id
                ORDER BY p.name
                """
            ),
            {"therapist_id": therapist_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def find(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                SELECT p.id, p.therapist_id, p.name, p.age, p.gender,
                       p.email, p.phone, p.condition,
                       MAX(b.appointment_date) FILTER (WHERE b.status = 'completed')
                           AS last_session_date,
                       p.created_at, p.updated_at
                FROM patients p
                LEFT JOIN bookings b ON b.patient_id = p.id
                LEFT JOIN schedule_slots s ON s.id = b.slot_id
                WHERE p.id = :patient_id
                  AND p.therapist_id = :therapist_id
                GROUP BY p.id
                """
            ),
            {"therapist_id": therapist_id, "patient_id": patient_id},
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def create(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        request: PatientRequest,
    ) -> dict[str, Any]:
        result = await connection.execute(
            text(
                """
                INSERT INTO patients (
                    therapist_id, name, age, gender, email, phone, condition
                )
                VALUES (
                    :therapist_id, :name, :age, :gender, :email, :phone,
                    :condition
                )
                RETURNING id, therapist_id, name, age, gender, email, phone,
                          condition, NULL::date AS last_session_date,
                          created_at, updated_at
                """
            ),
            {"therapist_id": therapist_id, **request.model_dump(mode="json")},
        )
        return dict(result.mappings().one())

    async def update(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
        request: PatientRequest,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                UPDATE patients
                SET name = :name, age = :age, gender = :gender,
                    email = :email, phone = :phone, condition = :condition,
                    updated_at = NOW()
                WHERE id = :patient_id AND therapist_id = :therapist_id
                RETURNING id, therapist_id, name, age, gender, email, phone,
                          condition, created_at, updated_at
                """
            ),
            {
                "therapist_id": therapist_id,
                "patient_id": patient_id,
                **request.model_dump(mode="json"),
            },
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def delete(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
    ) -> bool:
        result = await connection.execute(
            text(
                """
                DELETE FROM patients
                WHERE id = :patient_id AND therapist_id = :therapist_id
                RETURNING id
                """
            ),
            {"therapist_id": therapist_id, "patient_id": patient_id},
        )
        return result.mappings().first() is not None

    async def sessions(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT b.id AS booking_id, b.treatment, b.location, b.status,
                       b.appointment_date AS slot_date, s.start_time, s.end_time
                FROM bookings b
                JOIN schedule_slots s ON s.id = b.slot_id
                WHERE b.patient_id = :patient_id
                  AND b.therapist_id = :therapist_id
                ORDER BY b.appointment_date DESC, s.start_time DESC
                """
            ),
            {"therapist_id": therapist_id, "patient_id": patient_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def notes(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT n.id, n.patient_id, n.booking_id, n.note,
                       n.exercises, n.next_session, n.created_at,
                       n.updated_at
                FROM patient_notes n
                JOIN patients p ON p.id = n.patient_id
                WHERE n.patient_id = :patient_id
                  AND p.therapist_id = :therapist_id
                ORDER BY n.created_at DESC
                """
            ),
            {"therapist_id": therapist_id, "patient_id": patient_id},
        )
        return [dict(row) for row in result.mappings().all()]

    async def create_note(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
        request: PatientNoteRequest,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                INSERT INTO patient_notes (
                    patient_id, booking_id, note, exercises, next_session
                )
                SELECT :patient_id, :booking_id, :note, :exercises,
                       :next_session
                WHERE EXISTS (
                    SELECT 1 FROM patients
                    WHERE id = :patient_id AND therapist_id = :therapist_id
                )
                  AND (
                      CAST(:booking_id AS BIGINT) IS NULL
                      OR EXISTS (
                          SELECT 1 FROM bookings
                          WHERE id = :booking_id
                            AND therapist_id = :therapist_id
                            AND patient_id = :patient_id
                      )
                  )
                RETURNING id, patient_id, booking_id, note, exercises,
                          next_session, created_at, updated_at
                """
            ),
            {
                "therapist_id": therapist_id,
                "patient_id": patient_id,
                **request.model_dump(mode="json"),
            },
        )
        row = result.mappings().first()
        return dict(row) if row else None

    async def update_note(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        patient_id: int,
        note_id: int,
        request: PatientNoteRequest,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                UPDATE patient_notes n
                SET note = :note, exercises = :exercises,
                    next_session = :next_session, updated_at = NOW()
                FROM patients p
                WHERE n.patient_id = p.id
                  AND n.id = :note_id
                  AND n.patient_id = :patient_id
                  AND p.therapist_id = :therapist_id
                RETURNING n.id, n.patient_id, n.booking_id, n.note,
                          n.exercises, n.next_session, n.created_at,
                          n.updated_at
                """
            ),
            {
                "therapist_id": therapist_id,
                "patient_id": patient_id,
                "note_id": note_id,
                **request.model_dump(mode="json"),
            },
        )
        row = result.mappings().first()
        return dict(row) if row else None
