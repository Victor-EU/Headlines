from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class CategoryRedirect(Base):
    __tablename__ = "category_redirects"

    old_slug: Mapped[str] = mapped_column(String(100), primary_key=True)
    new_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    surface: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
