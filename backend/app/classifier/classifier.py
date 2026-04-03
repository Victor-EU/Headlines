from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.llm.registry import run_classify
from app.models import Article, ArticleCategory, Category, PipelineLog, Source

from .prompts import (
    CLASSIFICATION_SYSTEM_PROMPT,
    CLASSIFICATION_TOOL_SCHEMA,
    build_classification_prompt,
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 15
MAX_CLASSIFICATION_ATTEMPTS = 3


async def classify_batch(
    db: AsyncSession,
    source_ids: list | None = None,
    trigger: str = "scheduled",
) -> dict:
    """Classify unclassified articles. Returns stats dict."""
    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    # Collect unclassified articles
    q = (
        select(Article)
        .options(selectinload(Article.source))
        .where(Article.classified == False)
        .order_by(Article.published_at.asc())
    )
    if source_ids:
        q = q.where(Article.source_id.in_(source_ids))

    result = await db.execute(q)
    articles = list(result.scalars().all())

    if not articles:
        return {"articles_processed": 0, "articles_classified": 0}

    # Group by surface
    by_surface: dict[str, list[Article]] = {}
    for a in articles:
        surface = a.source.surface
        by_surface.setdefault(surface, []).append(a)

    total_processed = 0
    total_classified = 0
    total_uncategorized = 0
    total_failed = 0
    total_input_tokens = 0
    total_output_tokens = 0

    for surface, surface_articles in by_surface.items():
        # Load categories for this surface
        cat_result = await db.execute(
            select(Category).where(Category.surface == surface, Category.active == True)
        )
        categories = list(cat_result.scalars().all())
        cat_list = [{"slug": c.slug, "description": c.description} for c in categories]
        slug_to_id = {c.slug: c.id for c in categories}

        # Process in batches
        for i in range(0, len(surface_articles), BATCH_SIZE):
            batch = surface_articles[i : i + BATCH_SIZE]
            article_data = [
                {"id": str(a.id), "title": a.title, "summary": a.summary}
                for a in batch
            ]

            try:
                user_prompt = build_classification_prompt(article_data, cat_list)
                llm_result = await run_classify(
                    db, "classification", CLASSIFICATION_SYSTEM_PROMPT, user_prompt, CLASSIFICATION_TOOL_SCHEMA
                )

                total_input_tokens += llm_result.input_tokens
                total_output_tokens += llm_result.output_tokens

                # Map results by article_id
                result_map = {c.article_id: c for c in llm_result.classifications}

                for article in batch:
                    total_processed += 1
                    article_id_str = str(article.id)

                    item = result_map.get(article_id_str)
                    cats = item.categories if item else []
                    assigned = 0

                    for cat in cats:
                        slug = cat.get("slug", "")
                        confidence = cat.get("confidence", 0.0)

                        if confidence < 0.5:
                            continue
                        if slug not in slug_to_id:
                            continue

                        ac = ArticleCategory(
                            article_id=article.id,
                            category_id=slug_to_id[slug],
                            confidence=confidence,
                        )
                        db.add(ac)
                        assigned += 1

                        if assigned >= 3:
                            break

                    article.classified = True
                    article.interest_score = item.interest_score if item else None
                    if assigned > 0:
                        total_classified += 1
                    else:
                        total_uncategorized += 1

            except Exception as e:
                logger.error(f"Classification batch failed: {e}")
                for article in batch:
                    article.classification_attempts = (article.classification_attempts or 0) + 1
                    total_processed += 1
                    if article.classification_attempts >= MAX_CLASSIFICATION_ATTEMPTS:
                        article.classified = True  # Give up after max retries
                    total_failed += 1

    # Write pipeline_log
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - start_time) * 1000)

    status = "success"
    if total_failed > 0 and total_classified == 0:
        status = "failed"
    elif total_failed > 0:
        status = "partial"

    pipeline_log = PipelineLog(
        task="classification",
        status=status,
        trigger=trigger,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        articles_processed=total_processed,
        articles_classified=total_classified,
        articles_uncategorized=total_uncategorized,
        articles_failed=total_failed,
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
    )
    db.add(pipeline_log)
    await db.flush()

    return {
        "articles_processed": total_processed,
        "articles_classified": total_classified,
        "articles_uncategorized": total_uncategorized,
        "articles_failed": total_failed,
    }
