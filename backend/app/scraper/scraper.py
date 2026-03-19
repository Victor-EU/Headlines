from __future__ import annotations

import logging
import traceback
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.registry import get_adapter
from app.models import Article, FetchLog, Source
from app.scraper.types import FetchResult

logger = logging.getLogger(__name__)

STALE_MINUTES = 5


async def scrape(
    db: AsyncSession,
    source: Source,
    trigger: str = "scheduled",
    batch_id: uuid.UUID | None = None,
) -> FetchResult:
    """Fetch articles from a source. Never throws — all errors recorded in fetch_log."""
    started_at = datetime.now(timezone.utc)

    try:
        # Check for in-flight fetch (concurrency guard)
        stale_cutoff = started_at - timedelta(minutes=STALE_MINUTES)
        running_q = await db.execute(
            select(FetchLog).where(
                FetchLog.source_id == source.id,
                FetchLog.status == "running",
                FetchLog.started_at > stale_cutoff,
            )
        )
        if running_q.scalar_one_or_none():
            return FetchResult(status="skipped", error="Fetch already in progress")

        # Expire stale "running" records (crash recovery)
        await db.execute(
            update(FetchLog)
            .where(
                FetchLog.source_id == source.id,
                FetchLog.status == "running",
                FetchLog.started_at <= stale_cutoff,
            )
            .values(
                status="failed",
                error_message="Expired: worker likely crashed",
                finished_at=started_at,
            )
        )

        # Create fetch_log
        fetch_log = FetchLog(
            source_id=source.id,
            batch_id=batch_id,
            status="running",
            trigger=trigger,
            started_at=started_at,
        )
        db.add(fetch_log)
        await db.flush()

        # Call adapter
        adapter = get_adapter(source.adapter_type)
        result = await adapter.fetch(source)

        fetch_log.http_status = result.http_status
        fetch_log.response_bytes = result.response_bytes

        # Handle 304
        if result.http_status == 304:
            finished_at = datetime.now(timezone.utc)
            fetch_log.status = "success"
            fetch_log.finished_at = finished_at
            fetch_log.duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            source.last_fetched_at = finished_at
            source.last_error = None
            source.consecutive_failures = 0
            await db.commit()
            return FetchResult(
                fetch_log_id=fetch_log.id,
                status="success",
                duration_ms=fetch_log.duration_ms,
            )

        fetch_log.articles_in_feed = len(result.articles)

        # Test mode — skip upsert, return raw articles
        if trigger == "test":
            finished_at = datetime.now(timezone.utc)
            fetch_log.status = "success"
            fetch_log.finished_at = finished_at
            fetch_log.duration_ms = int((finished_at - started_at).total_seconds() * 1000)
            await db.commit()
            return FetchResult(
                fetch_log_id=fetch_log.id,
                status="success",
                articles_in_feed=len(result.articles),
                duration_ms=fetch_log.duration_ms,
                articles=result.articles,
            )

        # Upsert articles
        new_count = 0
        updated_count = 0
        skipped_count = 0
        failed_count = 0
        new_article_ids = []

        for raw in result.articles:
            try:
                stmt = (
                    pg_insert(Article)
                    .values(
                        source_id=source.id,
                        external_id=raw.external_id,
                        title=raw.title,
                        url=raw.url,
                        summary=raw.summary,
                        author=raw.author,
                        image_url=raw.image_url,
                        published_at=raw.published_at,
                    )
                    .on_conflict_do_update(
                        constraint="uq_articles_source_external",
                        set_={
                            "title": raw.title,
                            "summary": raw.summary,
                            "updated_at": datetime.now(timezone.utc),
                        },
                        where=(
                            (Article.title != raw.title) | (Article.summary != raw.summary)
                        ),
                    )
                    .returning(Article.id, Article.created_at, Article.updated_at)
                )
                row = (await db.execute(stmt)).first()

                if row is None:
                    skipped_count += 1
                elif row.created_at == row.updated_at:
                    # Newly inserted
                    new_count += 1
                    new_article_ids.append(row.id)
                else:
                    updated_count += 1
            except Exception as e:
                failed_count += 1
                logger.warning(f"Failed to upsert article '{raw.title}': {e}")

        # Update source record
        finished_at = datetime.now(timezone.utc)
        source.last_fetched_at = finished_at
        source.last_etag = result.etag
        source.last_modified = result.last_modified
        source.last_error = None
        source.consecutive_failures = 0

        # Finalize fetch_log
        status = "success"
        if failed_count > 0 and new_count == 0 and updated_count == 0:
            status = "failed"
        elif failed_count > 0:
            status = "partial"

        fetch_log.status = status
        fetch_log.finished_at = finished_at
        fetch_log.duration_ms = int((finished_at - started_at).total_seconds() * 1000)
        fetch_log.articles_new = new_count
        fetch_log.articles_updated = updated_count
        fetch_log.articles_skipped = skipped_count
        fetch_log.articles_failed = failed_count

        if result.errors:
            fetch_log.error_message = "; ".join(result.errors[:5])

        await db.commit()

        return FetchResult(
            fetch_log_id=fetch_log.id,
            status=status,
            articles_in_feed=len(result.articles),
            articles_new=new_count,
            articles_updated=updated_count,
            articles_skipped=skipped_count,
            articles_failed=failed_count,
            duration_ms=fetch_log.duration_ms,
            new_article_ids=new_article_ids,
        )

    except Exception as e:
        logger.error(f"Scrape failed for {source.name}: {e}")
        tb = traceback.format_exc()

        # Try to record the failure
        try:
            finished_at = datetime.now(timezone.utc)
            source.last_error = str(e)
            source.consecutive_failures += 1

            fetch_log_err = FetchLog(
                source_id=source.id,
                batch_id=batch_id,
                status="failed",
                trigger=trigger,
                started_at=started_at,
                finished_at=finished_at,
                duration_ms=int((finished_at - started_at).total_seconds() * 1000),
                error_message=str(e),
                error_traceback=tb,
            )
            db.add(fetch_log_err)
            await db.commit()
        except Exception:
            await db.rollback()

        return FetchResult(
            status="failed",
            error=str(e),
            duration_ms=int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000),
        )
