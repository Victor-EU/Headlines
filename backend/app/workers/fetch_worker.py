from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FetchLog, Source
from app.scraper.scraper import scrape

logger = logging.getLogger(__name__)

_last_batch_at: datetime | None = None
BATCH_COOLDOWN_SECONDS = 60
CONCURRENCY_LIMIT = 10


async def start_batch_refresh(db: AsyncSession) -> dict:
    """Refresh all active sources concurrently. Returns batch status."""
    global _last_batch_at

    now = datetime.now(timezone.utc)
    if _last_batch_at and (now - _last_batch_at).total_seconds() < BATCH_COOLDOWN_SECONDS:
        return {"error": "Batch refresh on cooldown", "cooldown_remaining": BATCH_COOLDOWN_SECONDS - int((now - _last_batch_at).total_seconds())}

    _last_batch_at = now
    batch_id = uuid.uuid4()

    result = await db.execute(
        select(Source).where(Source.active == True)
    )
    sources = list(result.scalars().all())

    if not sources:
        return {"batch_id": batch_id, "sources_triggered": 0, "sources_skipped": 0}

    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

    async def _scrape_one(source: Source):
        async with sem:
            from app.database import async_session
            async with async_session() as session:
                return await scrape(session, source, trigger="batch", batch_id=batch_id)

    results = await asyncio.gather(
        *[_scrape_one(s) for s in sources],
        return_exceptions=True,
    )

    triggered = 0
    skipped = 0
    new_article_ids = []

    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Batch scrape error: {r}")
            continue
        if r.status == "skipped":
            skipped += 1
        else:
            triggered += 1
            new_article_ids.extend(r.new_article_ids)

    # Trigger classification + dedup for new articles
    if new_article_ids:
        from app.database import async_session
        async with async_session() as session:
            from app.classifier.classifier import classify_batch
            await classify_batch(session, trigger="batch")

            from app.dedup import dedup_batch
            await dedup_batch(session, new_article_ids, trigger="batch")

            await session.commit()

    return {
        "batch_id": batch_id,
        "sources_triggered": triggered,
        "sources_skipped": skipped,
    }
