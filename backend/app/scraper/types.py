from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from app.adapters.base import RawArticle


@dataclass
class FetchResult:
    fetch_log_id: uuid.UUID | None = None
    status: str = "success"
    articles_in_feed: int = 0
    articles_new: int = 0
    articles_updated: int = 0
    articles_skipped: int = 0
    articles_failed: int = 0
    duration_ms: int = 0
    error: str | None = None
    articles: list[RawArticle] | None = None
    new_article_ids: list[uuid.UUID] = field(default_factory=list)
