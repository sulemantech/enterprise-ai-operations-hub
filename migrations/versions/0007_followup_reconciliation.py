"""record operator reconciliation of uncertain follow-up delivery

Revision ID: 0007
Revises: 0006
"""

from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "followup_delivery_status_valid", "followup_deliveries", type_="check"
    )
    op.create_check_constraint(
        "followup_delivery_status_valid",
        "followup_deliveries",
        "status IN ('sending', 'sent', 'rejected', 'unknown', 'confirmed_not_sent')",
    )
    op.add_column("followup_deliveries", sa.Column("reconciled_by", sa.Text))
    op.add_column(
        "followup_deliveries",
        sa.Column("reconciled_at", sa.DateTime(timezone=True)),
    )
    op.add_column("followup_deliveries", sa.Column("reconciliation_note", sa.Text))


def downgrade() -> None:
    op.execute(
        "UPDATE followup_deliveries SET status = 'unknown' WHERE status = 'confirmed_not_sent'"
    )
    op.drop_column("followup_deliveries", "reconciliation_note")
    op.drop_column("followup_deliveries", "reconciled_at")
    op.drop_column("followup_deliveries", "reconciled_by")
    op.drop_constraint(
        "followup_delivery_status_valid", "followup_deliveries", type_="check"
    )
    op.create_check_constraint(
        "followup_delivery_status_valid",
        "followup_deliveries",
        "status IN ('sending', 'sent', 'rejected', 'unknown')",
    )
