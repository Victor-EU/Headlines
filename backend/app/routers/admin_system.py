from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.admin import get_admin
from app.database import get_db
from app.models import Article, Briefing, FetchLog, PipelineLog, Source
from app.schemas.admin import BriefingAdminResponse, RegenerateRequest

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-system"],
    dependencies=[Depends(get_admin)],
)


@router.get("/system/status")
async def system_status(db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)
    last_24h = now - timedelta(hours=24)

    # Source health
    sources_q = await db.execute(select(Source).order_by(Source.name))
    sources = []
    for s in sources_q.scalars().all():
        articles_24h = await db.scalar(
            select(func.count(Article.id)).where(
                Article.source_id == s.id, Article.fetched_at >= last_24h
            )
        )
        status = "healthy"
        if s.consecutive_failures >= 5:
            status = "error"
        elif s.consecutive_failures >= 2:
            status = "warning"
        elif not s.active:
            status = "disabled"

        sources.append(
            {
                "name": s.name,
                "last_fetch": s.last_fetched_at.isoformat() if s.last_fetched_at else None,
                "status": status,
                "consecutive_failures": s.consecutive_failures,
                "articles_last_24h": articles_24h or 0,
            }
        )

    # Pipeline task status
    task_names = ["classification", "dedup", "briefing", "learning_digest", "analysis"]
    tasks = []
    for task_name in task_names:
        last_log_q = await db.execute(
            select(PipelineLog)
            .where(PipelineLog.task == task_name)
            .order_by(PipelineLog.started_at.desc())
            .limit(1)
        )
        last_log = last_log_q.scalar_one_or_none()
        tasks.append(
            {
                "task": task_name,
                "last_run": last_log.started_at.isoformat() if last_log else None,
                "status": last_log.status if last_log else "never_run",
                "model_used": last_log.model_used if last_log else None,
            }
        )

    # Cost tracking
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    today_cost = await db.scalar(
        select(func.sum(PipelineLog.estimated_cost_usd)).where(
            PipelineLog.started_at >= today_start
        )
    ) or 0.0

    month_cost = await db.scalar(
        select(func.sum(PipelineLog.estimated_cost_usd)).where(
            PipelineLog.started_at >= month_start
        )
    ) or 0.0

    cost_by_task = {}
    for task_name in task_names:
        task_cost = await db.scalar(
            select(func.sum(PipelineLog.estimated_cost_usd)).where(
                PipelineLog.task == task_name,
                PipelineLog.started_at >= month_start,
            )
        ) or 0.0
        cost_by_task[task_name] = round(task_cost, 6)

    # Briefing status
    from app.models import Briefing

    latest_news = await db.execute(
        select(Briefing)
        .where(Briefing.type == "daily_news")
        .order_by(Briefing.date.desc())
        .limit(1)
    )
    news_brief = latest_news.scalar_one_or_none()

    latest_learning = await db.execute(
        select(Briefing)
        .where(Briefing.type == "weekly_learning")
        .order_by(Briefing.date.desc())
        .limit(1)
    )
    learning_brief = latest_learning.scalar_one_or_none()

    # Queue depth
    queue_depth = await db.scalar(
        select(func.count(Article.id)).where(Article.classified == False)
    ) or 0

    return {
        "sources": sources,
        "tasks": tasks,
        "costs": {
            "today_usd": round(today_cost, 6),
            "this_month_usd": round(month_cost, 6),
            "by_task": cost_by_task,
        },
        "briefings": {
            "daily_news": {
                "date": str(news_brief.date) if news_brief else None,
                "generated_at": news_brief.generated_at.isoformat()
                if news_brief and news_brief.generated_at
                else None,
                "model": news_brief.brief_model if news_brief else None,
            },
            "weekly_learning": {
                "date": str(learning_brief.date) if learning_brief else None,
                "generated_at": learning_brief.generated_at.isoformat()
                if learning_brief and learning_brief.generated_at
                else None,
                "model": learning_brief.brief_model if learning_brief else None,
            },
        },
        "queue_depth": queue_depth,
    }


@router.get("/system/errors")
async def system_errors(db: AsyncSession = Depends(get_db)):
    last_24h = datetime.now(timezone.utc) - timedelta(hours=24)

    # Failed/partial fetch logs
    fetch_errors_q = await db.execute(
        select(FetchLog, Source.name)
        .join(Source, FetchLog.source_id == Source.id)
        .where(
            FetchLog.started_at >= last_24h,
            FetchLog.status.in_(["failed", "partial"]),
        )
        .order_by(FetchLog.started_at.desc())
        .limit(50)
    )
    fetch_errors = [
        {
            "type": "fetch",
            "source_name": name,
            "status": log.status,
            "error": log.error_message,
            "at": log.started_at.isoformat(),
        }
        for log, name in fetch_errors_q.all()
    ]

    # Failed/partial pipeline logs
    pipeline_errors_q = await db.execute(
        select(PipelineLog)
        .where(
            PipelineLog.started_at >= last_24h,
            PipelineLog.status.in_(["failed", "partial"]),
        )
        .order_by(PipelineLog.started_at.desc())
        .limit(50)
    )
    pipeline_errors = [
        {
            "type": "pipeline",
            "task": log.task,
            "status": log.status,
            "error": log.error_message,
            "at": log.started_at.isoformat(),
        }
        for log in pipeline_errors_q.scalars().all()
    ]

    return {"errors": fetch_errors + pipeline_errors}


@router.get("/briefings", response_model=list[BriefingAdminResponse])
async def list_briefings(db: AsyncSession = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(Briefing)
        .where(Briefing.generated_at >= cutoff)
        .order_by(Briefing.date.desc())
    )
    briefings = list(result.scalars().all())
    return [
        BriefingAdminResponse(
            id=b.id,
            type=b.type,
            date=str(b.date),
            brief=b.brief,
            brief_model=b.brief_model,
            generated_at=b.generated_at,
            article_ids=b.article_ids or [],
            focus_topic=b.focus_topic,
            focus_body=b.focus_body,
            focus_model=b.focus_model,
        )
        for b in briefings
    ]


@router.post("/briefings/regenerate")
async def regenerate_briefing(
    body: RegenerateRequest, db: AsyncSession = Depends(get_db)
):
    if body.type == "daily_news":
        from app.editorial.briefing import generate_briefing

        result = await generate_briefing(db, trigger="manual", force=True)
    elif body.type == "weekly_learning":
        from app.editorial.learning_digest import generate_learning_digest

        result = await generate_learning_digest(db, trigger="manual", force=True)
    elif body.type == "analysis":
        from app.editorial.analysis import generate_analysis

        result = await generate_analysis(db, trigger="manual", force=True)
    else:
        raise HTTPException(400, f"Unknown briefing type: {body.type}")

    return result
