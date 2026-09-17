from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.features.booking.schemas import CreateBookingRequest


class BookingRepository:
    async def list_available_therapists(
        self,
        connection: AsyncConnection,
        selected_date: date,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT t.id, t.name, t.username,
                       p.profile_image_url, p.experience_years,
                       p.specialization, p.address,
                       s.id AS slot_id, :selected_date AS slot_date,
                       s.start_time, s.end_time
                FROM users t
                JOIN therapist_availability a
                  ON a.therapist_id = t.id
                 AND a.is_available = TRUE
                LEFT JOIN profiles p ON p.therapist_id = t.id
                JOIN schedule_slots s
                  ON s.therapist_id = t.id
                 AND s.day_of_week = (
                     EXTRACT(ISODOW FROM CAST(:selected_date AS DATE))::INT - 1
                 )
                 AND s.status = 'open'
                WHERE t.is_active = TRUE
                  AND t.user_type = 'therapist'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM bookings b
                      WHERE b.slot_id = s.id
                        AND b.appointment_date = :selected_date
                        AND b.status NOT IN ('declined', 'cancelled')
                  )
                ORDER BY t.name, s.start_time
                """
            ),
            {"selected_date": selected_date},
        )
        return [dict(row) for row in result.mappings().all()]

    async def list_available_slots(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        selected_date: date,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT s.id, :selected_date AS slot_date, s.start_time, s.end_time
                FROM schedule_slots s
                JOIN therapist_availability a ON a.therapist_id = s.therapist_id
                WHERE s.therapist_id = :therapist_id
                  AND s.day_of_week = (
                      EXTRACT(ISODOW FROM CAST(:selected_date AS DATE))::INT - 1
                  )
                  AND s.status = 'open'
                  AND a.is_available = TRUE
                  AND NOT EXISTS (
                      SELECT 1
                      FROM bookings b
                      WHERE b.slot_id = s.id
                        AND b.appointment_date = :selected_date
                        AND b.status NOT IN ('declined', 'cancelled')
                  )
                ORDER BY s.start_time
                """
            ),
            {
                "therapist_id": therapist_id,
                "selected_date": selected_date,
            },
        )
        return [dict(row) for row in result.mappings().all()]

    async def reserve_slot_and_create_booking(
        self,
        connection: AsyncConnection,
        request: CreateBookingRequest,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                WITH patient AS (
                    INSERT INTO patients (
                        therapist_id, name, age, gender, email, phone, condition
                    )
                    VALUES (
                        :therapist_id, :patient_name, :patient_age,
                        :patient_gender, :patient_email, :patient_phone,
                        COALESCE(:patient_condition, :treatment)
                    )
                    ON CONFLICT (therapist_id, email)
                    WHERE email IS NOT NULL
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        age = COALESCE(EXCLUDED.age, patients.age),
                        gender = COALESCE(EXCLUDED.gender, patients.gender),
                        phone = EXCLUDED.phone,
                        condition = EXCLUDED.condition,
                        updated_at = NOW()
                    RETURNING id
                )
                INSERT INTO bookings (
                    therapist_id, patient_id, slot_id, appointment_date, patient_name,
                    patient_email, patient_phone, treatment, location
                )
                SELECT
                    :therapist_id, patient.id, s.id, :slot_date, :patient_name,
                    :patient_email, :patient_phone, :treatment, :location
                FROM schedule_slots AS s
                JOIN therapist_availability AS a
                 ON a.therapist_id = s.therapist_id
                 AND a.is_available = TRUE
                CROSS JOIN patient
                WHERE s.id = :slot_id
                  AND s.therapist_id = :therapist_id
                  AND s.day_of_week = (
                      EXTRACT(ISODOW FROM CAST(:slot_date AS DATE))::INT - 1
                  )
                  AND s.status = 'open'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM bookings existing
                      WHERE existing.slot_id = s.id
                        AND existing.appointment_date = :slot_date
                        AND existing.status NOT IN ('declined', 'cancelled')
                  )
                RETURNING id
                """
            ),
            request.model_dump(mode="json"),
        )
        booking = result.mappings().first()
        if not booking:
            return None
        result = await connection.execute(
            text(
                """
                SELECT b.id, b.therapist_id, b.patient_id, b.slot_id,
                       b.appointment_date AS slot_date, b.patient_name,
                       b.patient_email, b.patient_phone, b.treatment,
                       b.location, b.status, b.therapist_notes,
                       s.start_time,
                       s.end_time, b.created_at, b.updated_at
                FROM bookings b
                JOIN schedule_slots s ON s.id = b.slot_id
                WHERE b.id = :booking_id
                """
            ),
            {"booking_id": booking["id"]},
        )
        return dict(result.mappings().one())

    async def list_for_therapist(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        booking_status: str | None = None,
    ) -> list[dict[str, Any]]:
        result = await connection.execute(
            text(
                """
                SELECT b.id, b.therapist_id, b.patient_id, b.slot_id,
                       b.appointment_date AS slot_date, b.patient_name,
                       b.patient_email, b.patient_phone, b.treatment,
                       b.location, b.status, b.therapist_notes,
                       s.start_time,
                       s.end_time, b.created_at, b.updated_at
                FROM bookings b
                JOIN schedule_slots s ON s.id = b.slot_id
                WHERE b.therapist_id = :therapist_id
                  AND (
                      CAST(:booking_status AS VARCHAR) IS NULL
                      OR b.status = :booking_status
                  )
                ORDER BY b.appointment_date, s.start_time, b.created_at
                """
            ),
            {"therapist_id": therapist_id, "booking_status": booking_status},
        )
        return [dict(row) for row in result.mappings().all()]

    async def update_status(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        booking_id: int,
        new_status: str,
    ) -> dict[str, Any] | None:
        allowed_from = {
            "accepted": "'pending'",
            "declined": "'pending'",
            "completed": "'accepted'",
            "cancelled": "'pending', 'accepted'",
        }[new_status]
        result = await connection.execute(
            text(
                f"""
                UPDATE bookings b
                SET status = :new_status, updated_at = NOW()
                FROM schedule_slots s
                WHERE b.slot_id = s.id
                  AND b.id = :booking_id
                  AND b.therapist_id = :therapist_id
                  AND b.status IN ({allowed_from})
                RETURNING b.id, b.therapist_id, b.patient_id, b.slot_id,
                          b.appointment_date AS slot_date, b.patient_name,
                          b.patient_email, b.patient_phone, b.treatment,
                          b.location, b.status, b.therapist_notes,
                          s.start_time,
                          s.end_time, b.created_at, b.updated_at
                """
            ),
            {
                "booking_id": booking_id,
                "therapist_id": therapist_id,
                "new_status": new_status,
            },
        )
        booking = result.mappings().first()
        if not booking:
            return None

        return dict(booking)

    async def reschedule(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        booking_id: int,
        new_slot_id: int,
        new_slot_date: date,
    ) -> dict[str, Any] | None:
        current_result = await connection.execute(
            text(
                """
                SELECT b.id, b.slot_id, b.appointment_date, b.status
                FROM bookings b
                JOIN schedule_slots s ON s.id = b.slot_id
                WHERE b.id = :booking_id
                  AND b.therapist_id = :therapist_id
                  AND b.status IN ('pending', 'accepted')
                FOR UPDATE OF b, s
                """
            ),
            {"booking_id": booking_id, "therapist_id": therapist_id},
        )
        current = current_result.mappings().first()
        if not current or (
            current["slot_id"] == new_slot_id
            and current["appointment_date"] == new_slot_date
        ):
            return None

        target_result = await connection.execute(
            text(
                """
                SELECT id, status
                FROM schedule_slots
                WHERE id = :new_slot_id
                  AND therapist_id = :therapist_id
                FOR UPDATE
                """
            ),
            {"new_slot_id": new_slot_id, "therapist_id": therapist_id},
        )
        target = target_result.mappings().first()
        if not target or target["status"] != "open":
            return None

        target_day_result = await connection.execute(
            text(
                """
                SELECT day_of_week
                FROM schedule_slots
                WHERE id = :new_slot_id
                """
            ),
            {"new_slot_id": new_slot_id},
        )
        target_day = target_day_result.scalar_one_or_none()
        if target_day is None or target_day != new_slot_date.weekday():
            return None

        active_booking = await connection.execute(
            text(
                """
                SELECT 1
                FROM bookings
                WHERE slot_id = :new_slot_id
                  AND appointment_date = :new_slot_date
                  AND status NOT IN ('declined', 'cancelled')
                """
            ),
            {"new_slot_id": new_slot_id, "new_slot_date": new_slot_date},
        )
        if active_booking.first():
            return None

        await connection.execute(
            text(
                """
                UPDATE bookings
                SET slot_id = :new_slot_id,
                    appointment_date = :new_slot_date,
                    updated_at = NOW()
                WHERE id = :booking_id
                """
            ),
            {
                "booking_id": booking_id,
                "new_slot_id": new_slot_id,
                "new_slot_date": new_slot_date,
            },
        )
        result = await connection.execute(
            text(
                """
                SELECT b.id, b.therapist_id, b.patient_id, b.slot_id,
                       b.appointment_date AS slot_date, b.patient_name,
                       b.patient_email, b.patient_phone, b.treatment,
                       b.location, b.status, b.therapist_notes,
                       s.start_time, s.end_time,
                       b.created_at, b.updated_at
                FROM bookings b
                JOIN schedule_slots s ON s.id = b.slot_id
                WHERE b.id = :booking_id
                """
            ),
            {"booking_id": booking_id},
        )
        return dict(result.mappings().one())

    async def update_notes(
        self,
        connection: AsyncConnection,
        therapist_id: int,
        booking_id: int,
        notes: str,
    ) -> dict[str, Any] | None:
        result = await connection.execute(
            text(
                """
                UPDATE bookings b
                SET therapist_notes = :notes, updated_at = NOW()
                FROM schedule_slots s
                WHERE b.slot_id = s.id
                  AND b.id = :booking_id
                  AND b.therapist_id = :therapist_id
                  AND b.status IN ('pending', 'accepted', 'completed')
                RETURNING b.id, b.therapist_id, b.patient_id, b.slot_id,
                          b.appointment_date AS slot_date, b.patient_name,
                          b.patient_email, b.patient_phone, b.treatment,
                          b.location, b.status, b.therapist_notes,
                          s.start_time, s.end_time,
                          b.created_at, b.updated_at
                """
            ),
            {
                "booking_id": booking_id,
                "therapist_id": therapist_id,
                "notes": notes,
            },
        )
        booking = result.mappings().first()
        return dict(booking) if booking else None
