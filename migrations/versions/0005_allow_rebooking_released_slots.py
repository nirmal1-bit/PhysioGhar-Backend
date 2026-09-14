"""allow rebooking declined and cancelled slots

Revision ID: 0005_rebook_released_slots
Revises: 0004_create_bookings
Create Date: 2026-09-14
"""

from alembic import op

revision = "0005_rebook_released_slots"
down_revision = "0004_create_bookings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("bookings_slot_id_key", "bookings", type_="unique")
    op.execute(
        """
        CREATE UNIQUE INDEX bookings_active_slot_unique
        ON bookings (slot_id)
        WHERE status NOT IN ('declined', 'cancelled')
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX bookings_active_slot_unique")
    op.create_unique_constraint("bookings_slot_id_key", "bookings", ["slot_id"])
