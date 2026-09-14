"""make profile phone optional

Revision ID: 0006_make_profile_phone_optional
Revises: 0005_rebook_released_slots
"""

from alembic import op


revision = "0006_make_profile_phone_optional"
down_revision = "0005_rebook_released_slots"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE profiles ALTER COLUMN phone DROP NOT NULL")


def downgrade() -> None:
    op.execute(
        """
        UPDATE profiles
        SET phone = 'Not provided'
        WHERE phone IS NULL
        """
    )
    op.execute("ALTER TABLE profiles ALTER COLUMN phone SET NOT NULL")
