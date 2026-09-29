"""Initial schema: policies, contractors, jobs and documents.

Revision ID: 0001
Revises:
Create Date: 2026-09-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # A policy can change over time, so (id, version) identifies one exact set of rules.
    op.create_table(
        "policies",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("version", sa.Integer, primary_key=True),
        sa.Column("required_types", postgresql.ARRAY(sa.Text), nullable=False),
        sa.Column("minimum_insurance_aud", sa.BigInteger, nullable=False),
    )

    op.create_table(
        "contractors",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("email", sa.Text, nullable=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("status", sa.Text, nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("policy_id", sa.Text, nullable=False),
        sa.Column("policy_version", sa.Integer, nullable=False),
        sa.ForeignKeyConstraint(
            ["policy_id", "policy_version"], ["policies.id", "policies.version"]
        ),
        sa.CheckConstraint("end_date >= start_date", name="job_dates_ordered"),
    )

    # A job can have several contractors and a contractor several jobs,
    # so the link gets its own table instead of a list column.
    op.create_table(
        "job_contractors",
        sa.Column("job_id", sa.Text, sa.ForeignKey("jobs.id"), primary_key=True),
        sa.Column(
            "contractor_id", sa.Text, sa.ForeignKey("contractors.id"), primary_key=True
        ),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Text, primary_key=True),
        sa.Column(
            "contractor_id", sa.Text, sa.ForeignKey("contractors.id"), nullable=False
        ),
        sa.Column("type", sa.Text, nullable=False),
        sa.Column("review_status", sa.Text, nullable=False),
        sa.Column("valid_from", sa.Date, nullable=False),
        sa.Column("valid_to", sa.Date, nullable=False),
        # Only insurance has an amount, so these may be empty.
        sa.Column("coverage_amount", sa.BigInteger),
        sa.Column("currency", sa.Text),
        sa.CheckConstraint("valid_to >= valid_from", name="document_dates_ordered"),
    )
    op.create_index("documents_contractor_id", "documents", ["contractor_id"])


def downgrade() -> None:
    op.drop_table("documents")
    op.drop_table("job_contractors")
    op.drop_table("jobs")
    op.drop_table("contractors")
    op.drop_table("policies")
