from __future__ import annotations

from pydantic import BaseModel


class OverviewResponse(BaseModel):
    period_days: int
    sessions: int
    page_views: int
    headline_clicks: int
    ctr: float
    new_sessions: int
    returning_sessions: int


class TopHeadlineItem(BaseModel):
    article_id: str
    title: str
    source_name: str
    clicks: int


class TopHeadlinesResponse(BaseModel):
    period_days: int
    headlines: list[TopHeadlineItem]


class SourceMetric(BaseModel):
    source_slug: str
    source_name: str | None = None
    clicks: int
    share: float


class BySourceResponse(BaseModel):
    period_days: int
    total_clicks: int
    sources: list[SourceMetric]


class CategoryMetric(BaseModel):
    category_slug: str
    clicks: int
    page_views: int
    ctr: float


class ByCategoryResponse(BaseModel):
    period_days: int
    categories: list[CategoryMetric]


class HourMetric(BaseModel):
    hour: int  # 0-23
    page_views: int
    clicks: int


class ByHourResponse(BaseModel):
    period_days: int
    hours: list[HourMetric]
