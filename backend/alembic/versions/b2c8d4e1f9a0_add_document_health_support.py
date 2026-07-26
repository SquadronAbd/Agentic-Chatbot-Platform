"""add document health support

Revision ID: b2c8d4e1f9a0
Revises: ae1f6fd84fde
Create Date: 2026-07-25 19:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c8d4e1f9a0"
down_revision: Union[str, Sequence[str], None] = "ae1f6fd84fde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("needs_reindex", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "document_health_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("reindex_requested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("orphans_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("orphans_deleted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("inconsistent_flagged", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("metadata_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("document_health_runs")
    op.drop_column("document_chunks", "needs_reindex")
