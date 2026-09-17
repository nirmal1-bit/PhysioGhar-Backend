"""create therapist patient records

Revision ID: 0004_create_patients
Revises: 0003_create_schedule
"""

from alembic import op

revision = "0004_create_patients"
down_revision = "0003_create_schedule"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE patients (
            id BIGSERIAL PRIMARY KEY,
            user_id BIGINT UNIQUE REFERENCES users(id) ON DELETE SET NULL,
            therapist_id BIGINT NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            name VARCHAR(120) NOT NULL,
            age INTEGER,
            gender VARCHAR(32),
            email VARCHAR(320),
            phone VARCHAR(32),
            condition VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT patients_age_check CHECK (age IS NULL OR age >= 0)
        )
        """
    )
    op.execute(
        "CREATE INDEX patients_therapist_index ON patients (therapist_id)"
    )
    op.execute(
        """
        CREATE UNIQUE INDEX patients_therapist_email_unique
        ON patients (therapist_id, email)
        WHERE email IS NOT NULL
        """
    )
    op.execute(
        """
        CREATE TABLE bookings (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            patient_id BIGINT REFERENCES patients(id) ON DELETE SET NULL,
            slot_id BIGINT NOT NULL
                REFERENCES schedule_slots(id) ON DELETE RESTRICT,
            appointment_date DATE NOT NULL,
            patient_name VARCHAR(120) NOT NULL,
            patient_email VARCHAR(320) NOT NULL,
            patient_phone VARCHAR(32) NOT NULL,
            treatment VARCHAR(255) NOT NULL,
            location VARCHAR(500) NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'pending',
            therapist_notes TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT bookings_status_check
                CHECK (status IN (
                    'pending', 'accepted', 'completed', 'declined', 'cancelled'
                ))
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX bookings_active_occurrence_unique
        ON bookings (slot_id, appointment_date)
        WHERE status NOT IN ('declined', 'cancelled')
        """
    )
    op.execute(
        """
        CREATE INDEX bookings_therapist_status_index
        ON bookings (therapist_id, status)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE bookings")
    op.execute("DROP INDEX patients_therapist_email_unique")
    op.execute("DROP TABLE patients")
