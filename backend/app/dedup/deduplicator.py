from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.llm.registry import run_dedup
from app.models import Article, PipelineLog, PipelineTask, Source

from .prompts import DEDUP_SYSTEM_PROMPT, DEDUP_TOOL_SCHEMA, build_dedup_prompt
from .similarity import jaccard_similarity, normalize_title

logger = logging.getLogger(__name__)


async def dedup_batch(
    db: AsyncSession,
    article_ids: list[uuid.UUID],
    trigger: str = "scheduled",
) -> dict:
    """Deduplicate a batch of newly classified articles. Returns stats dict."""
    started_at = datetime.now(timezone.utc)
    start_time = time.monotonic()

    # Check if dedup task is active
    task = await db.get(PipelineTask, "dedup")
    if not task or not task.active:
        return {"articles_processed": 0, "duplicates_found": 0, "skipped": True}

    config = task.config or {}
    threshold = config.get("similarity_threshold", 0.35)
    window_hours = config.get("window_hours", 48)
    max_candidates = config.get("max_candidates", 5)

    # Load articles to process, sorted by published_at ASC (sequential processing)
    result = await db.execute(
        select(Article)
        .options(selectinload(Article.source))
        .where(Article.id.in_(article_ids))
        .order_by(Article.published_at.asc())
    )
    articles = list(result.scalars().all())

    if not articles:
        return {"articles_processed": 0, "duplicates_found": 0}

    total_processed = 0
    duplicates_found = 0
    clusters_created = 0
    clusters_updated = 0
    total_input_tokens = 0
    total_output_tokens = 0
    failed = 0
    semantic_fallback_used = 0

    for article in articles:
        total_processed += 1

        try:
            # Phase 1: Find Jaccard candidates
            article_tokens = normalize_title(article.title)

            if len(article_tokens) < 3:
                # Too short for meaningful Jaccard
                article.cluster_id = uuid.uuid4()
                clusters_created += 1
                continue

            window_start = datetime.now(timezone.utc) - timedelta(hours=window_hours)
            candidates_q = await db.execute(
                select(Article)
                .options(selectinload(Article.source))
                .where(
                    Article.source.has(Source.surface == article.source.surface),
                    Article.source_id != article.source_id,
                    Article.is_representative == True,
                    Article.published_at > window_start,
                    Article.id != article.id,
                )
            )
            recent_articles = list(candidates_q.scalars().all())

            candidates = []
            for candidate in recent_articles:
                cand_tokens = normalize_title(candidate.title)
                if len(cand_tokens) < 3:
                    continue
                sim = jaccard_similarity(article_tokens, cand_tokens)
                if sim >= threshold:
                    candidates.append((sim, candidate))

            candidates.sort(key=lambda x: x[0], reverse=True)
            candidates = candidates[:max_candidates]

            if not candidates:
                if config.get("semantic_fallback", True):
                    max_semantic = config.get("max_semantic_candidates", 15)
                    fallback_sorted = sorted(
                        recent_articles,
                        key=lambda a: a.published_at,
                        reverse=True,
                    )[:max_semantic]
                    if fallback_sorted:
                        candidates = [(0.0, a) for a in fallback_sorted]
                        semantic_fallback_used += 1

                if not candidates:
                    article.cluster_id = uuid.uuid4()
                    clusters_created += 1
                    continue

            # Phase 2: LLM confirmation
            article_data = {
                "id": str(article.id),
                "title": article.title,
                "source": article.source.name,
            }
            candidate_data = [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "source": c.source.name,
                }
                for _, c in candidates
            ]

            user_prompt = build_dedup_prompt(article_data, candidate_data)
            llm_result = await run_dedup(
                db, "dedup", DEDUP_SYSTEM_PROMPT, user_prompt, DEDUP_TOOL_SCHEMA
            )

            total_input_tokens += llm_result.input_tokens
            total_output_tokens += llm_result.output_tokens

            if llm_result.result and llm_result.result.is_duplicate and llm_result.result.duplicate_of:
                # Find the matching candidate
                match_id = llm_result.result.duplicate_of
                match_article = None
                for _, c in candidates:
                    if str(c.id) == match_id:
                        match_article = c
                        break

                if match_article:
                    duplicates_found += 1

                    # Assign cluster
                    if match_article.cluster_id:
                        article.cluster_id = match_article.cluster_id
                    else:
                        new_cluster = uuid.uuid4()
                        match_article.cluster_id = new_cluster
                        article.cluster_id = new_cluster

                    # Representative swap
                    best_id = llm_result.result.best_representative
                    if best_id == str(article.id):
                        article.is_representative = True
                        match_article.is_representative = False
                    else:
                        article.is_representative = False

                    clusters_updated += 1
                else:
                    # LLM returned an ID we don't recognize
                    article.cluster_id = uuid.uuid4()
                    clusters_created += 1
            else:
                article.cluster_id = uuid.uuid4()
                clusters_created += 1

        except Exception as e:
            logger.error(f"Dedup failed for article {article.id}: {e}")
            article.cluster_id = uuid.uuid4()
            clusters_created += 1
            failed += 1

    # Write pipeline_log
    finished_at = datetime.now(timezone.utc)
    duration_ms = int((time.monotonic() - start_time) * 1000)

    status = "success"
    if failed > 0 and duplicates_found == 0 and clusters_created == 0:
        status = "failed"
    elif failed > 0:
        status = "partial"

    pipeline_log = PipelineLog(
        task="dedup",
        status=status,
        trigger=trigger,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        articles_processed=total_processed,
        articles_classified=duplicates_found,
        articles_failed=failed,
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
    )
    db.add(pipeline_log)
    await db.flush()

    return {
        "articles_processed": total_processed,
        "duplicates_found": duplicates_found,
        "clusters_created": clusters_created,
        "clusters_updated": clusters_updated,
        "semantic_fallback_used": semantic_fallback_used,
    }


async def hide_article(db: AsyncSession, article_id: uuid.UUID) -> None:
    """Hide an article. If it's a representative, promote next-best in cluster."""
    article = await db.get(Article, article_id)
    if not article:
        return

    article.hidden = True

    if article.is_representative and article.cluster_id:
        # Find next best in cluster
        result = await db.execute(
            select(Article)
            .where(
                Article.cluster_id == article.cluster_id,
                Article.id != article.id,
                Article.hidden == False,
            )
            .order_by(Article.published_at.desc())
            .limit(1)
        )
        next_rep = result.scalar_one_or_none()
        if next_rep:
            next_rep.is_representative = True
            article.is_representative = False
