from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawArticle:
    external_id: str
    title: str
    url: str
    summary: str | None = None
    author: str | None = None
    image_url: str | None = None
    published_at: datetime | None = None


@dataclass
class AdapterResult:
    articles: list[RawArticle] = field(default_factory=list)
    http_status: int | None = None
    etag: str | None = None
    last_modified: str | None = None
    response_bytes: int | None = None
    errors: list[str] = field(default_factory=list)


class BaseAdapter(ABC):
    @abstractmethod
    async def fetch(self, source) -> AdapterResult:
        ...
