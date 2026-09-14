"""create booking requests

Revision ID: 0004_create_bookings
Revises: 0003_create_schedule
Create Date: 2026-09-14
"""

from alembic import op

revision = "0004_create_bookings"
down_revision = "0003_create_schedule"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE bookings (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL
                REFERENCES therapists(id) ON DELETE CASCADE,
            slot_id BIGINT NOT NULL UNIQUE
                REFERENCES schedule_slots(id) ON DELETE RESTRICT,
            patient_name VARCHAR(120) NOT NULL,
            patient_email VARCHAR(320) NOT NULL,
            patient_phone VARCHAR(32) NOT NULL,
            treatment VARCHAR(255) NOT NULL,
            location VARCHAR(500) NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'pending',
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
        CREATE INDEX bookings_therapist_status_index
        ON bookings (therapist_id, status)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE bookings")

