"""Descriptive columns for a richer demo: job title and site, contractor trade.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Nullable: they describe records but no rule depends on them.
    op.add_column("jobs", sa.Column("title", sa.Text))
    op.add_column("jobs", sa.Column("site", sa.Text))
    op.add_column("contractors", sa.Column("trade", sa.Text))
    op.create_index("jobs_dates", "jobs", ["start_date", "end_date"])


def downgrade() -> None:
    op.drop_index("jobs_dates", table_name="jobs")
    op.drop_column("contractors", "trade")
    op.drop_column("jobs", "site")
    op.drop_column("jobs", "title")
