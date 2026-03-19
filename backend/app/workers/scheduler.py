import asyncio
import logging
import random
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select, update

from app.config import settings
from app.database import async_session
from app.models import FetchLog, PipelineLog, Source
from app.scraper.scraper import scrape
from app.workers.alerting import check_source_alert, send_daily_error_summary
from app.workers.retention_worker import run_retention

logger = logging.getLogger(__name__)


async def _expire_stale_records():
    """On startup: expire any stale 'running' records from crashed workers."""
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        await db.execute(
            update(FetchLog)
            .where(FetchLog.status == "running")
            .values(
                status="failed",
                error_message="Expired on worker restart",
                finished_at=now,
            )
        )
        await db.execute(
            update(PipelineLog)
            .where(PipelineLog.status == "running")
            .values(
                status="failed",
                error_message="Expired on worker restart",
                finished_at=now,
            )
        )
        await db.commit()
    logger.info("Expired stale running records")


async def _tick():
    """Main scheduler tick — fetch due sources, classify, dedup."""
    async with async_session() as db:
        now = datetime.now(timezone.utc)

        # Find sources due for fetch (active only!)
        result = await db.execute(
            select(Source).where(
                Source.active == True,
                (
                    Source.last_fetched_at.is_(None)
                    | (
                        Source.last_fetched_at
                        <= now - timedelta(minutes=1)  # will be refined per source below
                    )
                ),
            )
        )
        sources = list(result.scalars().all())

        for source in sources:
            # Check if source is actually due
            if source.last_fetched_at:
                next_fetch = source.last_fetched_at + timedelta(minutes=source.fetch_interval)
                if now < next_fetch:
                    continue

            logger.info(f"Fetching: {source.name}")

            try:
                fetch_result = await scrape(db, source, trigger="scheduled")

                if fetch_result.articles_new > 0:
                    logger.info(f"  {fetch_result.articles_new} new articles from {source.name}")

                    # Classify new articles
                    from app.classifier.classifier import classify_batch
                    await classify_batch(db, source_ids=[source.id], trigger="scheduled")

                    # Dedup new articles
                    if fetch_result.new_article_ids:
                        from app.dedup import dedup_batch
                        await dedup_batch(db, fetch_result.new_article_ids, trigger="scheduled")

                await db.commit()

                # After commit: check if today's news briefing needs generating
                if fetch_result.articles_new > 0 and source.surface == "news":
                    try:
                        async with async_session() as briefing_db:
                            from app.editorial import generate_briefing
                            result = await generate_briefing(briefing_db, trigger="post_classify")
                            await briefing_db.commit()
                            if result.get("status") == "success":
                                logger.info("Post-classification briefing generated")
                    except Exception as e:
                        logger.error(f"Post-classification briefing check failed: {e}")

            except Exception as e:
                logger.error(f"Error processing {source.name}: {e}")
                await db.rollback()
                continue

            # Check for source failure alert (after successful commit)
            if fetch_result.status == "failed":
                try:
                    await check_source_alert(source.name, source.consecutive_failures)
                except Exception:
                    pass


async def _run_briefing():
    """Scheduled daily news briefing generation."""
    async with async_session() as db:
        try:
            from app.editorial import generate_briefing
            result = await generate_briefing(db, trigger="scheduled")
            await db.commit()
            logger.info(f"Briefing generation: {result}")
        except Exception as e:
            logger.error(f"Briefing generation failed: {e}")
            await db.rollback()


async def _run_learning_digest():
    """Scheduled weekly learning digest generation."""
    async with async_session() as db:
        try:
            from app.editorial import generate_learning_digest
            result = await generate_learning_digest(db, trigger="scheduled")
            await db.commit()
            logger.info(f"Learning digest generation: {result}")
        except Exception as e:
            logger.error(f"Learning digest generation failed: {e}")
            await db.rollback()


async def _run_analysis():
    """Scheduled daily In Focus analysis generation."""
    async with async_session() as db:
        try:
            from app.editorial import generate_analysis
            result = await generate_analysis(db, trigger="scheduled")
            await db.commit()
            logger.info(f"Analysis generation: {result}")
        except Exception as e:
            logger.error(f"Analysis generation failed: {e}")
            await db.rollback()


async def start_scheduler() -> AsyncIOScheduler:
    await _expire_stale_records()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(_tick, "interval", seconds=60, id="main_tick", max_instances=1)

    # Daily news briefing at 6:30 AM in configured timezone
    scheduler.add_job(
        _run_briefing,
        CronTrigger(hour=6, minute=30, timezone=settings.BRIEFING_TIMEZONE),
        id="daily_briefing",
        max_instances=1,
    )

    # Weekly learning digest Monday 7:00 AM in configured timezone
    scheduler.add_job(
        _run_learning_digest,
        CronTrigger(day_of_week="mon", hour=7, minute=0, timezone=settings.BRIEFING_TIMEZONE),
        id="weekly_learning_digest",
        max_instances=1,
    )

    # Daily In Focus analysis at 7:00 AM in configured timezone
    scheduler.add_job(
        _run_analysis,
        CronTrigger(hour=7, minute=0, timezone=settings.BRIEFING_TIMEZONE),
        id="daily_analysis",
        max_instances=1,
    )

    # Daily retention cleanup at 3:00 AM UTC
    scheduler.add_job(
        run_retention,
        CronTrigger(hour=3, minute=0, timezone="UTC"),
        id="daily_retention",
        max_instances=1,
    )

    # Daily error summary at 7:00 AM UTC
    scheduler.add_job(
        send_daily_error_summary,
        CronTrigger(hour=7, minute=0, timezone="UTC"),
        id="daily_error_summary",
        max_instances=1,
    )

    # Stagger initial fetch by delaying the first tick
    initial_delay = random.uniform(0, 30)
    scheduler.add_job(
        _tick,
        "date",
        run_date=datetime.now(timezone.utc) + timedelta(seconds=initial_delay),
        id="initial_tick",
    )

    scheduler.start()
    return scheduler
