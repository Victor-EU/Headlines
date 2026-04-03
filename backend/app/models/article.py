from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, SmallInteger, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from .article_category import ArticleCategory
    from .source import Source


class Article(TimestampMixin, Base):
    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_articles_source_external"),
        Index("idx_articles_published_at", "published_at", postgresql_using="btree"),
        Index("idx_articles_unclassified", "id", postgresql_where="classified = false"),
        Index(
            "idx_articles_reader",
            "published_at",
            postgresql_where="hidden = false AND is_representative = true",
        ),
        Index("idx_articles_cluster", "cluster_id", postgresql_where="cluster_id IS NOT NULL"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )
    external_id: Mapped[str] = mapped_column(Text, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    classified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    cluster_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    is_representative: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    interest_score: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    classification_attempts: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")

    source: Mapped["Source"] = relationship(back_populates="articles", lazy="raise")
    article_categories: Mapped[List["ArticleCategory"]] = relationship(
        back_populates="article", lazy="raise"
    )
