from __future__ import annotations

import uuid

from pydantic import BaseModel


class AnalyticsEventCreate(BaseModel):
    event_type: str
    article_id: uuid.UUID | None = None
    category_slug: str | None = None
    source_slug: str | None = None
    surface: str | None = None
    session_id: str
    referrer: str | None = None
