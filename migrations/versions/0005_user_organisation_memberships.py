"""Add OIDC subject-to-organisation role assignments.

Revision ID: 0005
Revises: 0004
"""

from alembic import op
import sqlalchemy as sa

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_organisation_memberships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("issuer", sa.Text, nullable=False),
        sa.Column("subject", sa.Text, nullable=False),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("role", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.UniqueConstraint(
            "issuer", "subject", "organisation_id", name="uq_user_org_membership"
        ),
        sa.CheckConstraint("role IN ('viewer', 'manager')", name="membership_role_valid"),
    )
    op.create_index(
        "ix_membership_identity_active",
        "user_organisation_memberships",
        ["issuer", "subject", "active"],
    )


def downgrade() -> None:
    op.drop_index("ix_membership_identity_active", "user_organisation_memberships")
    op.drop_table("user_organisation_memberships")
