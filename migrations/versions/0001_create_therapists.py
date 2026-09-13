"""create therapists table

Revision ID: 0001_create_therapists
Revises:
Create Date: 2026-09-13
"""

from alembic import op

revision = "0001_create_therapists"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE therapists (
            id BIGSERIAL PRIMARY KEY,
            email VARCHAR(254) NOT NULL,
            name VARCHAR(120) NOT NULL,
            username VARCHAR(50) NOT NULL,
            password_hash TEXT NOT NULL,
            user_type VARCHAR(32) NOT NULL DEFAULT 'therapist',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT therapists_user_type_check
                CHECK (user_type = 'therapist')
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX therapists_email_lower_unique
        ON therapists (LOWER(email))
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX therapists_username_lower_unique
        ON therapists (LOWER(username))
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE therapists")
