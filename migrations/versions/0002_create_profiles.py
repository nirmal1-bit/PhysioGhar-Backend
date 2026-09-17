"""create therapist profiles

Revision ID: 0002_create_profiles
Revises: 0001_create_users
"""

from alembic import op

revision = "0002_create_profiles"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE profiles (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL UNIQUE
                REFERENCES users(id) ON DELETE CASCADE,
            profile_image_url TEXT,
            phone VARCHAR(32),
            experience_years INTEGER NOT NULL,
            specialization VARCHAR(255) NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT profiles_experience_years_check
                CHECK (experience_years >= 0)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE profiles")
