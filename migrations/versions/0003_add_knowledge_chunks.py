"""add knowledge chunks

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-02 10:23:05.624748

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import VECTOR


# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.create_table(
        "knowledge_chunks",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organisation_id", sa.Text, nullable=False),
        sa.Column("policy_id", sa.Text, nullable=False),
        sa.Column("policy_version", sa.Integer, nullable=False),
        sa.Column("document_id", sa.Text, nullable=False),
        sa.Column("document_version", sa.Integer, nullable=False),
        sa.Column("section_id", sa.Text, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("source_path", sa.Text, nullable=False),
        sa.Column("source_status", sa.Text, nullable=False),
        sa.Column("synthetic", sa.Boolean, nullable=False),
        sa.Column("implementation_scope", sa.Text, nullable=False),
        sa.Column("embedding_model", sa.Text, nullable=False),
        sa.Column("content_hash", sa.Text, nullable=False),
        sa.Column("embedding", VECTOR(1024), nullable=False),
        sa.UniqueConstraint(
            "organisation_id",
            "policy_id",
            "policy_version",
            "document_id",
            "document_version",
            "section_id",
            "embedding_model",
            name="uq_knowledge_chunk_source_model",
        )
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("knowledge_chunks")
