"""add followup approvals

Revision ID: 0004
Revises: 7aa4b9901955
Create Date: 2026-10-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '7aa4b9901955'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # One row per approval. Rows are never updated: an edit after approval
    # returns the draft to 'draft', and approving again adds a new row.
    op.create_table(
        "followup_approvals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "draft_id", sa.Integer,
            sa.ForeignKey("followup_drafts.id"), nullable=False,
        ),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("approved_by", sa.Text, nullable=False),
        sa.Column(
            "approved_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        # A copy of exactly what was approved, and its fingerprint.
        sa.Column("recipient", sa.Text, nullable=False),
        sa.Column("subject", sa.Text, nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("fingerprint", sa.Text, nullable=False),
    )
    op.create_index(
        "ix_followup_approvals_draft_id", "followup_approvals", ["draft_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_followup_approvals_draft_id", "followup_approvals")
    op.drop_table("followup_approvals")
