"""category_composite_slug_surface_and_classification_retry

Revision ID: 007
Revises: 006
Create Date: 2026-04-03

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Category slug: global unique → per-surface unique
    op.drop_constraint("categories_slug_key", "categories", type_="unique")
    op.create_unique_constraint("uq_categories_slug_surface", "categories", ["slug", "surface"])

    # CategoryRedirect PK: old_slug → (old_slug, surface)
    op.drop_constraint("category_redirects_pkey", "category_redirects", type_="primary")
    op.create_primary_key("category_redirects_pkey", "category_redirects", ["old_slug", "surface"])

    # Classification retry tracking
    op.add_column("articles", sa.Column("classification_attempts", sa.SmallInteger(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("articles", "classification_attempts")
    op.drop_constraint("category_redirects_pkey", "category_redirects", type_="primary")
    op.create_primary_key("category_redirects_pkey", "category_redirects", ["old_slug"])
    op.drop_constraint("uq_categories_slug_surface", "categories", type_="unique")
    op.create_unique_constraint("categories_slug_key", "categories", ["slug"])
