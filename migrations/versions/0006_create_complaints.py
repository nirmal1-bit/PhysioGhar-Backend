"""create therapist complaints

Revision ID: 0006_create_complaints
Revises: 0005_create_patient_notes
"""

from alembic import op

revision = "0006_create_complaints"
down_revision = "0005_create_patient_notes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE complaints (
            id BIGSERIAL PRIMARY KEY,
            therapist_id BIGINT NOT NULL
                REFERENCES users(id) ON DELETE CASCADE,
            category VARCHAR(32) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            status VARCHAR(32) NOT NULL DEFAULT 'open',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT complaints_category_check CHECK (
                category IN (
                    'patient_issue', 'booking_issue', 'payment_issue',
                    'technical_issue', 'other'
                )
            ),
            CONSTRAINT complaints_status_check CHECK (
                status IN ('open', 'in_review', 'resolved')
            )
        )
        """
    )
    op.execute(
        """
        CREATE INDEX complaints_therapist_created_index
        ON complaints (therapist_id, created_at DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE complaints")
