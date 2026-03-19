from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.config import settings
from app.llm.registry import run_generate
from app.models import (
    Article,
    ArticleCategory,
    Briefing,
    LLMModel,
    PipelineLog,
    PipelineTask,
    Source,
)

from .prompts import LEARNING_DIGEST_SYSTEM_PROMPT, build_learning_digest_prompt

logger = logging.getLogger(__name__)

MIN_ARTICLES = 3


async def generate_learning_digest(
    db: AsyncSession,
    trigger: str = "scheduled",
    force: bool = False,
) -> dict:
    """Generate a weekly learning digest. Returns stats dict."""
    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    # Check if learning_digest task is active
    task = await db.get(PipelineTask, "learning_digest")
    if not task or not task.active:
        return {"status": "skipped", "reason": "task_inactive"}

    # Determine this week's Monday in configured timezone
    tz = ZoneInfo(settings.BRIEFING_TIMEZONE)
    today = datetime.now(tz).date()
    monday = today - timedelta(days=today.weekday())

    # Idempotency check
    if not force:
        existing = await db.execute(
            select(Briefing).where(
                Briefing.type == "weekly_learning",
                Briefing.date == monday,
            )
        )
        if existing.scalar_one_or_none():
            return {"status": "skipped", "reason": "already_exists"}

    # Collect this week's learning articles (last 7 days)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    q = (
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .options(
            joinedload(Article.source),
            selectinload(Article.article_categories).selectinload(
                ArticleCategory.category
            ),
        )
        .where(
            Source.surface == "learning",
            Article.classified == True,
            Article.is_representative == True,
            Article.hidden == False,
            Article.fetched_at >= cutoff,
        )
        .order_by(Article.published_at.desc())
    )
    result = await db.execute(q)
    articles = list(result.unique().scalars().all())

    if len(articles) < MIN_ARTICLES:
        return {
            "status": "skipped",
            "reason": "insufficient_articles",
            "articles_found": len(articles),
            "min_required": MIN_ARTICLES,
        }

    # Build article data (includes summaries for learning)
    article_data = []
    for a in articles:
        cats = [ac.category.slug for ac in a.article_categories]
        article_data.append(
            {
                "title": a.title,
                "source_name": a.source.name,
                "categories": cats,
                "summary": a.summary,
            }
        )

    # Build prompts
    config = task.config or {}
    max_sentences = config.get("max_sentences", 5)
    system_prompt = LEARNING_DIGEST_SYSTEM_PROMPT.format(max_sentences=max_sentences)
    user_prompt = build_learning_digest_prompt(article_data, config)

    # Generate via LLM
    gen_result = await run_generate(db, "learning_digest", system_prompt, user_prompt)

    # Look up model for cost calculation
    model_result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == task.model_id)
    )
    model = model_result.scalar_one()
    estimated_cost = (
        gen_result.input_tokens * model.input_price_per_mtok
        + gen_result.output_tokens * model.output_price_per_mtok
    ) / 1_000_000

    # Upsert digest
    article_ids = [a.id for a in articles]
    stmt = (
        pg_insert(Briefing)
        .values(
            type="weekly_learning",
            date=monday,
            brief=gen_result.text,
            article_ids=article_ids,
            brief_model=task.model_id,
            generated_at=datetime.now(timezone.utc),
        )
        .on_conflict_do_update(
            constraint="uq_briefings_type_date",
            set_={
                "brief": gen_result.text,
                "article_ids": article_ids,
                "brief_model": task.model_id,
                "generated_at": datetime.now(timezone.utc),
            },
        )
    )
    await db.execute(stmt)

    # Write pipeline log
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - start_time) * 1000)

    pipeline_log = PipelineLog(
        task="learning_digest",
        status="success",
        trigger=trigger,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        articles_processed=len(articles),
        model_used=task.model_id,
        input_tokens=gen_result.input_tokens,
        output_tokens=gen_result.output_tokens,
        estimated_cost_usd=estimated_cost,
    )
    db.add(pipeline_log)
    await db.flush()

    return {
        "status": "success",
        "date": str(monday),
        "articles": len(articles),
        "input_tokens": gen_result.input_tokens,
        "output_tokens": gen_result.output_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
    }
