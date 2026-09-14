"""merge profile and booking migrations

Revision ID: 0007_merge_profile_booking
Revises: 0006_add_booking_notes, 0006_make_profile_phone_optional
"""

revision = "0007_merge_profile_booking"
down_revision = (
    "0006_add_booking_notes",
    "0006_make_profile_phone_optional",
)
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
