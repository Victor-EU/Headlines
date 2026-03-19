import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete

from app.database import async_session
from app.models import AnalyticsEvent, Article, Briefing, FetchLog, PipelineLog

logger = logging.getLogger(__name__)


async def run_retention():
    """Delete old articles (30d), briefings (30d), logs (90d), analytics (90d)."""
    now = datetime.now(timezone.utc)
    cutoff_30d = now - timedelta(days=30)
    cutoff_90d = now - timedelta(days=90)

    async with async_session() as db:
        try:
            r1 = await db.execute(
                delete(Article).where(Article.published_at < cutoff_30d)
            )
            r2 = await db.execute(
                delete(Briefing).where(Briefing.date < cutoff_30d.date())
            )
            r3 = await db.execute(
                delete(FetchLog).where(FetchLog.started_at < cutoff_90d)
            )
            r4 = await db.execute(
                delete(PipelineLog).where(PipelineLog.started_at < cutoff_90d)
            )
            r5 = await db.execute(
                delete(AnalyticsEvent).where(AnalyticsEvent.created_at < cutoff_90d)
            )
            await db.commit()

            logger.info(
                "Retention cleanup: articles=%d briefings=%d fetch_logs=%d pipeline_logs=%d analytics=%d",
                r1.rowcount, r2.rowcount, r3.rowcount, r4.rowcount, r5.rowcount,
            )
        except Exception:
            await db.rollback()
            logger.exception("Retention cleanup failed")
