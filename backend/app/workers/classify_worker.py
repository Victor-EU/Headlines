from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.classifier.classifier import classify_batch

logger = logging.getLogger(__name__)


async def run_classification(db: AsyncSession, source_ids: list | None = None, trigger: str = "scheduled"):
    logger.info("Starting classification run...")
    result = await classify_batch(db, source_ids=source_ids, trigger=trigger)
    logger.info(
        f"Classification complete: {result['articles_processed']} processed, "
        f"{result['articles_classified']} classified"
    )
    return result
