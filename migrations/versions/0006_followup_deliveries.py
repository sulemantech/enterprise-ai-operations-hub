"""track approved follow-up delivery attempts

Revision ID: 0006
Revises: 0005
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "followup_deliveries",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "draft_id",
            sa.Integer,
            sa.ForeignKey("followup_drafts.id"),
            nullable=False,
        ),
        sa.Column(
            "approval_id",
            sa.Integer,
            sa.ForeignKey("followup_approvals.id"),
            nullable=False,
            unique=True,
        ),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("idempotency_key", sa.Text, nullable=False, unique=True),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("http_status", sa.Integer, nullable=True),
        sa.Column("response_payload", JSONB, nullable=True),
        sa.Column("error_code", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "status IN ('sending', 'sent', 'rejected', 'unknown')",
            name="followup_delivery_status_valid",
        ),
    )
    op.create_index(
        "ix_followup_deliveries_draft_org",
        "followup_deliveries",
        ["draft_id", "organisation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_followup_deliveries_draft_org", "followup_deliveries")
    op.drop_table("followup_deliveries")
