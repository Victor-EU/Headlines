import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import func, select

from app.config import settings
from app.database import async_session
from app.models import FetchLog, PipelineLog, Source

logger = logging.getLogger(__name__)


async def notify_slack(message: str):
    """Post a message to the configured Slack webhook. No-op if not configured."""
    if not settings.SLACK_WEBHOOK_URL:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(settings.SLACK_WEBHOOK_URL, json={"text": message})
    except Exception:
        logger.exception("Failed to send Slack notification")


async def check_source_alert(source_name: str, consecutive_failures: int):
    """Send alert when a source crosses the 5-failure threshold."""
    if consecutive_failures == 5:
        await notify_slack(
            f":warning: Source *{source_name}* has failed {consecutive_failures} times in a row."
        )


async def send_daily_error_summary():
    """Send a daily summary of errors from the last 24h. Exits early if nothing to report."""
    if not settings.SLACK_WEBHOOK_URL:
        return

    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    async with async_session() as db:
        try:
            fetch_errors = (await db.execute(
                select(func.count()).select_from(FetchLog).where(
                    FetchLog.started_at >= since,
                    FetchLog.status == "failed",
                )
            )).scalar() or 0

            pipeline_errors = (await db.execute(
                select(func.count()).select_from(PipelineLog).where(
                    PipelineLog.started_at >= since,
                    PipelineLog.status == "failed",
                )
            )).scalar() or 0

            failing_sources = (await db.execute(
                select(Source.name, Source.consecutive_failures).where(
                    Source.consecutive_failures >= 5,
                    Source.active == True,
                )
            )).all()

            if not fetch_errors and not pipeline_errors and not failing_sources:
                return

            lines = [":bar_chart: *Daily Error Summary*"]
            if fetch_errors:
                lines.append(f"• {fetch_errors} fetch error(s) in the last 24h")
            if pipeline_errors:
                lines.append(f"• {pipeline_errors} pipeline error(s) in the last 24h")
            if failing_sources:
                names = ", ".join(f"{name} ({count})" for name, count in failing_sources)
                lines.append(f"• Failing sources: {names}")

            await notify_slack("\n".join(lines))
        except Exception:
            logger.exception("Failed to send daily error summary")
