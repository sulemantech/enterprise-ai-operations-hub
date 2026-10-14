"""add followup drafts

Revision ID: 7aa4b9901955
Revises: 0003
Create Date: 2026-10-08 14:55:34.534618

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '7aa4b9901955'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "followup_drafts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("job_id", sa.Text, nullable=False),
        sa.Column("contractor_id", sa.Text, nullable=False),
        sa.Column(
            "status", sa.Text, nullable=False,
            server_default="draft",
        ),
        sa.Column("recipient", sa.Text, nullable=False),
        sa.Column("subject", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("assessment_status", sa.Text, nullable=False),
        sa.Column("reason", sa.Text, nullable=False),
        sa.Column("policy_id", sa.Text, nullable=False),
        sa.Column("policy_version", sa.Integer, nullable=False),
        sa.Column("evidence_ids", JSONB, nullable=False),
        sa.Column("source_snapshot", JSONB, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

def downgrade() -> None:
    op.drop_table("followup_drafts")