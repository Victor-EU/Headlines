"""add_surface_to_analytics

Revision ID: 004
Revises: 003
Create Date: 2026-03-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("analytics_events", sa.Column("surface", sa.Text(), nullable=True))
    op.create_index("idx_analytics_surface", "analytics_events", ["surface", "created_at"])


def downgrade() -> None:
    op.drop_index("idx_analytics_surface", table_name="analytics_events")
    op.drop_column("analytics_events", "surface")
