"""initial_schema

Revision ID: 001
Revises:
Create Date: 2026-03-16

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("surface", sa.Text(), nullable=False, server_default="news"),
        sa.Column("homepage_url", sa.Text(), nullable=False),
        sa.Column("feed_url", sa.Text(), nullable=False),
        sa.Column("adapter_type", sa.Text(), nullable=False, server_default="rss"),
        sa.Column("adapter_config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("fetch_interval", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("last_fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_etag", sa.Text(), nullable=True),
        sa.Column("last_modified", sa.Text(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("surface", sa.Text(), nullable=False, server_default="news"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "category_redirects",
        sa.Column("old_slug", sa.String(100), nullable=False),
        sa.Column("new_slug", sa.String(100), nullable=False),
        sa.Column("surface", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("old_slug"),
    )

    op.create_table(
        "llm_models",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.Text(), nullable=False),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("input_price_per_mtok", sa.Float(), nullable=True),
        sa.Column("output_price_per_mtok", sa.Float(), nullable=True),
        sa.Column("context_window", sa.Integer(), nullable=True),
        sa.Column("max_output_tokens", sa.Integer(), nullable=True),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("model_id"),
    )

    op.create_table(
        "pipeline_tasks",
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("model_id", sa.String(100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("task"),
        sa.ForeignKeyConstraint(["model_id"], ["llm_models.model_id"]),
    )

    op.create_table(
        "articles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.Text(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("classified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("hidden", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_representative", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("source_id", "external_id", name="uq_articles_source_external"),
    )
    op.create_index("idx_articles_published_at", "articles", ["published_at"])
    op.create_index("idx_articles_unclassified", "articles", ["id"], postgresql_where=sa.text("classified = false"))
    op.create_index("idx_articles_reader", "articles", ["published_at"], postgresql_where=sa.text("hidden = false AND is_representative = true"))
    op.create_index("idx_articles_cluster", "articles", ["cluster_id"], postgresql_where=sa.text("cluster_id IS NOT NULL"))

    op.create_table(
        "article_categories",
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("article_id", "category_id"),
        sa.ForeignKeyConstraint(["article_id"], ["articles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_article_categories_category", "article_categories", ["category_id"])

    op.create_table(
        "fetch_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("batch_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("trigger", sa.Text(), nullable=False, server_default="scheduled"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("response_bytes", sa.Integer(), nullable=True),
        sa.Column("articles_in_feed", sa.Integer(), server_default="0"),
        sa.Column("articles_new", sa.Integer(), server_default="0"),
        sa.Column("articles_updated", sa.Integer(), server_default="0"),
        sa.Column("articles_skipped", sa.Integer(), server_default="0"),
        sa.Column("articles_failed", sa.Integer(), server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("error_traceback", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_fetch_logs_source", "fetch_logs", ["source_id", "started_at"])
    op.create_index("idx_fetch_logs_status", "fetch_logs", ["status"], postgresql_where=sa.text("status != 'success'"))
    op.create_index("idx_fetch_logs_started", "fetch_logs", ["started_at"])
    op.create_index("idx_fetch_logs_batch", "fetch_logs", ["batch_id"], postgresql_where=sa.text("batch_id IS NOT NULL"))

    op.create_table(
        "pipeline_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task", sa.Text(), nullable=False, server_default="classification"),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("trigger", sa.Text(), nullable=False, server_default="scheduled"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("articles_processed", sa.Integer(), server_default="0"),
        sa.Column("articles_classified", sa.Integer(), server_default="0"),
        sa.Column("articles_uncategorized", sa.Integer(), server_default="0"),
        sa.Column("articles_failed", sa.Integer(), server_default="0"),
        sa.Column("model_used", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_pipeline_logs_started", "pipeline_logs", ["started_at"])
    op.create_index("idx_pipeline_logs_task", "pipeline_logs", ["task", "started_at"])
    op.create_index("idx_pipeline_logs_status", "pipeline_logs", ["status"], postgresql_where=sa.text("status != 'success'"))

    op.create_table(
        "briefings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("brief", sa.Text(), nullable=True),
        sa.Column("article_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("brief_model", sa.Text(), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("type", "date", name="uq_briefings_type_date"),
    )

    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("article_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category_slug", sa.Text(), nullable=True),
        sa.Column("source_slug", sa.Text(), nullable=True),
        sa.Column("session_id", sa.Text(), nullable=False),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_analytics_created", "analytics_events", ["created_at"])
    op.create_index("idx_analytics_session", "analytics_events", ["session_id"])
    op.create_index("idx_analytics_type", "analytics_events", ["event_type", "created_at"])


def downgrade() -> None:
    op.drop_table("analytics_events")
    op.drop_table("briefings")
    op.drop_table("pipeline_logs")
    op.drop_table("fetch_logs")
    op.drop_table("article_categories")
    op.drop_table("articles")
    op.drop_table("pipeline_tasks")
    op.drop_table("llm_models")
    op.drop_table("category_redirects")
    op.drop_table("categories")
    op.drop_table("sources")
