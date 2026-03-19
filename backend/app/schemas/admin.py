from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


# --- Auth ---
class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    token: str


# --- Sources ---
class SourceCreate(BaseModel):
    name: str
    slug: str
    surface: str = "news"
    homepage_url: str
    feed_url: str
    adapter_type: str = "rss"
    adapter_config: dict = {}
    fetch_interval: int = 15


class SourceUpdate(BaseModel):
    name: str | None = None
    homepage_url: str | None = None
    feed_url: str | None = None
    adapter_type: str | None = None
    adapter_config: dict | None = None
    fetch_interval: int | None = None
    active: bool | None = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    surface: str
    homepage_url: str
    feed_url: str
    adapter_type: str
    fetch_interval: int
    active: bool
    last_fetched_at: datetime | None = None
    last_error: str | None = None
    consecutive_failures: int = 0


class BatchRefreshResponse(BaseModel):
    batch_id: uuid.UUID
    sources_triggered: int
    sources_skipped: int


class FetchLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    status: str
    trigger: str
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: int | None = None
    articles_in_feed: int = 0
    articles_new: int = 0
    articles_updated: int = 0
    articles_failed: int = 0
    error_message: str | None = None


class TestFetchArticle(BaseModel):
    external_id: str
    title: str
    url: str
    summary: str | None = None
    published_at: datetime | None = None


# --- Categories ---
class CategoryCreate(BaseModel):
    name: str
    surface: str
    description: str


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    active: bool | None = None


class CategoryAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    surface: str
    description: str
    display_order: int
    active: bool
    article_count: int = 0


class ReorderItem(BaseModel):
    id: uuid.UUID
    display_order: int


class MergeRequest(BaseModel):
    target_id: uuid.UUID


class PreviewRequest(BaseModel):
    description: str | None = None


class PreviewResult(BaseModel):
    would_match: list[dict] = []
    currently_matched: list[dict] = []


class ReclassifyRequest(BaseModel):
    since: str  # "24h" or "7d"
    surface: str | None = None


class ReclassifyProgress(BaseModel):
    job_id: str
    total: int
    processed: int
    status: str


# --- LLM Models ---
class LLMModelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    provider: str
    model_id: str
    display_name: str
    active: bool
    input_price_per_mtok: float | None = None
    output_price_per_mtok: float | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    config: dict = {}


class LLMModelCreate(BaseModel):
    provider: str
    model_id: str
    display_name: str
    input_price_per_mtok: float | None = None
    output_price_per_mtok: float | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    config: dict = {}


class LLMModelUpdate(BaseModel):
    display_name: str | None = None
    active: bool | None = None
    input_price_per_mtok: float | None = None
    output_price_per_mtok: float | None = None
    config: dict | None = None


# --- Pipeline Tasks ---
class PipelineTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task: str
    model_id: str
    active: bool
    config: dict = {}


class PipelineTaskUpdate(BaseModel):
    model_id: str | None = None
    active: bool | None = None
    config: dict | None = None


# --- Articles Admin ---
class ArticleCategoryDetail(BaseModel):
    slug: str
    confidence: float
    manual: bool = False


class ArticleAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    url: str
    source_name: str
    published_at: datetime
    classified: bool
    hidden: bool
    is_representative: bool
    categories: list[ArticleCategoryDetail] = []


class ArticleUpdate(BaseModel):
    hidden: bool | None = None
    categories: list[uuid.UUID] | None = None


class BulkArticleAction(BaseModel):
    action: str  # "hide", "unhide", "reclassify", "assign_category"
    article_ids: list[uuid.UUID]
    category_id: uuid.UUID | None = None


# --- Briefings ---
class BriefingAdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    type: str
    date: str
    brief: str | None = None
    brief_model: str | None = None
    generated_at: datetime | None = None
    article_ids: list[uuid.UUID] = []
    focus_topic: str | None = None
    focus_body: str | None = None
    focus_model: str | None = None


class RegenerateRequest(BaseModel):
    type: str  # "daily_news", "weekly_learning", or "analysis"
