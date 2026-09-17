"""create patient note history

Revision ID: 0005_create_patient_notes
Revises: 0004_create_patients
"""

from alembic import op

revision = "0005_create_patient_notes"
down_revision = "0004_create_patients"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE patient_notes (
            id BIGSERIAL PRIMARY KEY,
            patient_id BIGINT NOT NULL
                REFERENCES patients(id) ON DELETE CASCADE,
            booking_id BIGINT REFERENCES bookings(id) ON DELETE SET NULL,
            note TEXT NOT NULL,
            exercises TEXT,
            next_session TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE INDEX patient_notes_patient_index
        ON patient_notes (patient_id, created_at DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE patient_notes")
