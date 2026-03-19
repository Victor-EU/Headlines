"""add_focus_columns_and_analysis_task

Revision ID: 005
Revises: 004
Create Date: 2026-03-17

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("briefings", sa.Column("focus_topic", sa.Text(), nullable=True))
    op.add_column("briefings", sa.Column("focus_body", sa.Text(), nullable=True))
    op.add_column("briefings", sa.Column("focus_model", sa.Text(), nullable=True))

    op.execute("""
        INSERT INTO pipeline_tasks (task, model_id, active, config, updated_at)
        SELECT 'analysis', model_id, true, '{"min_sources": 3}'::jsonb, now()
        FROM pipeline_tasks
        WHERE task = 'briefing'
        ON CONFLICT DO NOTHING
    """)


def downgrade() -> None:
    op.execute("DELETE FROM pipeline_tasks WHERE task = 'analysis'")
    op.drop_column("briefings", "focus_model")
    op.drop_column("briefings", "focus_body")
    op.drop_column("briefings", "focus_topic")
