"""create recurring therapist availability

Revision ID: 0003_create_schedule
Revises: 0002_create_profiles
"""

from alembic import op

revision = "0003_create_schedule"
down_revision = "0002_create_profiles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE therapist_availability (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL UNIQUE
                REFERENCES users(id) ON DELETE CASCADE,
            is_available BOOLEAN NOT NULL DEFAULT TRUE,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE schedule_slots (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            day_of_week SMALLINT NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            status VARCHAR(16) NOT NULL DEFAULT 'open',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT schedule_slots_day_check
                CHECK (day_of_week BETWEEN 0 AND 6),
            CONSTRAINT schedule_slots_time_check
                CHECK (end_time > start_time),
            CONSTRAINT schedule_slots_status_check
                CHECK (status IN ('open', 'blocked')),
            CONSTRAINT schedule_slots_unique_time
                UNIQUE (therapist_id, day_of_week, start_time, end_time)
        )
        """
    )
    op.execute(
        """
        CREATE INDEX schedule_slots_therapist_day_index
        ON schedule_slots (therapist_id, day_of_week)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE schedule_slots")
    op.execute("DROP TABLE therapist_availability")
