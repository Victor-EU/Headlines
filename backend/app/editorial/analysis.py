from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import desc, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.config import settings
from app.llm.registry import run_generate
from app.models import Article, Briefing, LLMModel, PipelineLog, PipelineTask, Source

from .prompts import ANALYSIS_SYSTEM_PROMPT, build_analysis_prompt

logger = logging.getLogger(__name__)


async def generate_analysis(
    db: AsyncSession,
    trigger: str = "scheduled",
    force: bool = False,
) -> dict:
    """Generate an In Focus analysis for the top cross-source story. Returns stats dict."""
    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    task = await db.get(PipelineTask, "analysis")
    if not task or not task.active:
        return {"status": "skipped", "reason": "task_inactive"}

    tz = ZoneInfo(settings.BRIEFING_TIMEZONE)
    briefing_date = datetime.now(tz).date()

    # Idempotency: skip if focus_topic already set for today
    if not force:
        existing = await db.execute(
            select(Briefing).where(
                Briefing.type == "daily_news",
                Briefing.date == briefing_date,
            )
        )
        existing_briefing = existing.scalar_one_or_none()
        if existing_briefing and existing_briefing.focus_topic:
            return {"status": "skipped", "reason": "already_exists"}

    # Find the cluster with the most distinct sources in the last 24h
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    config = task.config or {}
    min_sources = config.get("min_sources", 3)

    top_cluster_q = (
        select(
            Article.cluster_id,
            func.count(Article.source_id.distinct()).label("source_count"),
        )
        .join(Source, Article.source_id == Source.id)
        .where(
            Source.surface == "news",
            Article.published_at >= cutoff,
            Article.classified == True,
            Article.hidden == False,
            Article.cluster_id.isnot(None),
        )
        .group_by(Article.cluster_id)
        .having(func.count(Article.source_id.distinct()) >= min_sources)
        .order_by(desc("source_count"))
        .limit(1)
    )
    result = await db.execute(top_cluster_q)
    row = result.first()

    if not row:
        return {"status": "skipped", "reason": "no_qualifying_cluster"}

    top_cluster_id = row.cluster_id

    # Collect all articles in this cluster
    cluster_q = (
        select(Article)
        .options(joinedload(Article.source))
        .where(
            Article.cluster_id == top_cluster_id,
            Article.hidden == False,
        )
        .order_by(Article.published_at.desc())
    )
    cluster_result = await db.execute(cluster_q)
    cluster_articles = list(cluster_result.unique().scalars().all())

    # Deduplicate per source: keep most recently published per source_id
    seen_sources: dict[uuid.UUID, Article] = {}
    for a in cluster_articles:
        existing = seen_sources.get(a.source_id)
        if not existing or a.published_at > existing.published_at:
            seen_sources[a.source_id] = a
    unique_articles = list(seen_sources.values())

    # Build article data for prompt
    article_data = [
        {
            "title": a.title,
            "source_name": a.source.name,
            "summary": a.summary,
            "url": a.url,
        }
        for a in unique_articles
    ]

    # Build prompts and generate
    system_prompt = ANALYSIS_SYSTEM_PROMPT
    user_prompt = build_analysis_prompt(article_data, config)

    gen_result = await run_generate(db, "analysis", system_prompt, user_prompt)

    # Parse output: split on first "---" line
    lines = gen_result.text.strip().split("\n")
    separator_idx = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            separator_idx = i
            break

    if separator_idx is not None:
        topic = "\n".join(lines[:separator_idx]).strip()
        body = "\n".join(lines[separator_idx + 1 :]).strip()
    else:
        topic = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""

    # Cost calculation
    model_result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == task.model_id)
    )
    model = model_result.scalar_one()
    estimated_cost = (
        gen_result.input_tokens * model.input_price_per_mtok
        + gen_result.output_tokens * model.output_price_per_mtok
    ) / 1_000_000

    # Upsert — only touch focus columns
    stmt = (
        pg_insert(Briefing)
        .values(
            type="daily_news",
            date=briefing_date,
            focus_topic=topic,
            focus_body=body,
            focus_model=task.model_id,
        )
        .on_conflict_do_update(
            constraint="uq_briefings_type_date",
            set_={
                "focus_topic": topic,
                "focus_body": body,
                "focus_model": task.model_id,
            },
        )
    )
    await db.execute(stmt)

    # Pipeline log
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - start_time) * 1000)

    pipeline_log = PipelineLog(
        task="analysis",
        status="success",
        trigger=trigger,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        articles_processed=len(unique_articles),
        model_used=task.model_id,
        input_tokens=gen_result.input_tokens,
        output_tokens=gen_result.output_tokens,
        estimated_cost_usd=estimated_cost,
    )
    db.add(pipeline_log)
    await db.flush()

    return {
        "status": "success",
        "date": str(briefing_date),
        "cluster_id": str(top_cluster_id),
        "sources": len(unique_articles),
        "topic": topic,
        "input_tokens": gen_result.input_tokens,
        "output_tokens": gen_result.output_tokens,
        "estimated_cost_usd": round(estimated_cost, 6),
    }
