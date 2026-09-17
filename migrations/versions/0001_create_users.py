"""create shared user accounts

Revision ID: 0001_create_users
Revises:
"""

from alembic import op

revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE users (
            id BIGSERIAL PRIMARY KEY,
            email VARCHAR(254) NOT NULL,
            name VARCHAR(120) NOT NULL,
            username VARCHAR(50) NOT NULL,
            password_hash TEXT NOT NULL,
            user_type VARCHAR(32) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT users_user_type_check
                CHECK (user_type IN ('therapist', 'patient'))
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX users_email_lower_unique ON users (LOWER(email))"
    )
    op.execute(
        "CREATE UNIQUE INDEX users_username_lower_unique ON users (LOWER(username))"
    )


def downgrade() -> None:
    op.execute("DROP TABLE users")
