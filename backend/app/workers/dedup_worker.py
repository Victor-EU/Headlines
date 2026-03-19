from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.dedup import dedup_batch

logger = logging.getLogger(__name__)


async def run_dedup(db: AsyncSession, article_ids: list[uuid.UUID], trigger: str = "scheduled"):
    logger.info(f"Starting dedup run for {len(article_ids)} articles...")
    result = await dedup_batch(db, article_ids, trigger=trigger)
    if result.get("skipped"):
        logger.info("Dedup skipped (task inactive)")
    else:
        logger.info(
            f"Dedup complete: {result['articles_processed']} processed, "
            f"{result['duplicates_found']} duplicates found"
        )
    return result
