"""add therapist notes to bookings

Revision ID: 0006_add_booking_notes
Revises: 0005_rebook_released_slots
Create Date: 2026-09-15
"""

from alembic import op

revision = "0006_add_booking_notes"
down_revision = "0005_rebook_released_slots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE bookings ADD COLUMN therapist_notes TEXT"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE bookings DROP COLUMN therapist_notes")
