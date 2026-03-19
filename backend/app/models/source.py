from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, new_uuid

if TYPE_CHECKING:
    from .article import Article
    from .fetch_log import FetchLog


class Source(TimestampMixin, Base):
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    surface: Mapped[str] = mapped_column(Text, nullable=False, default="news")
    homepage_url: Mapped[str] = mapped_column(Text, nullable=False)
    feed_url: Mapped[str] = mapped_column(Text, nullable=False)
    adapter_type: Mapped[str] = mapped_column(Text, nullable=False, default="rss")
    adapter_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    fetch_interval: Mapped[int] = mapped_column(Integer, nullable=False, default=15)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_etag: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_modified: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    articles: Mapped[List["Article"]] = relationship(back_populates="source", lazy="raise")
    fetch_logs: Mapped[List["FetchLog"]] = relationship(back_populates="source", lazy="raise")
