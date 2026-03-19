from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .common import PaginationMeta


class AlsoReportedBy(BaseModel):
    source_name: str
    source_slug: str
    url: str


class HeadlineItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    summary: str | None = None
    source_name: str
    source_slug: str
    source_homepage: str
    published_at: datetime
    categories: list[str] = []
    also_reported_by: list[AlsoReportedBy] = []


class HeadlinesResponse(BaseModel):
    surface: str
    headlines: list[HeadlineItem]
    pagination: PaginationMeta


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    slug: str
    article_count: int = 0
