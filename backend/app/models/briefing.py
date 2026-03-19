from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from typing import List, Optional

from sqlalchemy import Date, DateTime, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, new_uuid


class Briefing(Base):
    __tablename__ = "briefings"
    __table_args__ = (UniqueConstraint("type", "date", name="uq_briefings_type_date"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    brief: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    article_ids: Mapped[Optional[List[uuid.UUID]]] = mapped_column(ARRAY(UUID(as_uuid=True)), nullable=True)
    brief_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    focus_topic: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    focus_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    focus_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
