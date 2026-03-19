from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, extract, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.admin import get_admin
from app.database import get_db
from app.models import AnalyticsEvent, Article, Source
from app.schemas.analytics import (
    ByCategoryResponse,
    ByHourResponse,
    BySourceResponse,
    CategoryMetric,
    HourMetric,
    OverviewResponse,
    SourceMetric,
    TopHeadlineItem,
    TopHeadlinesResponse,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-analytics"],
    dependencies=[Depends(get_admin)],
)


class Period(str, Enum):
    seven_days = "7d"
    thirty_days = "30d"
    ninety_days = "90d"


def _days(period: Period) -> int:
    return {"7d": 7, "30d": 30, "90d": 90}[period.value]


def _cutoff(period: Period) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=_days(period))


@router.get("/analytics/overview", response_model=OverviewResponse)
async def analytics_overview(
    db: AsyncSession = Depends(get_db),
    period: Period = Query(Period.seven_days),
):
    cutoff = _cutoff(period)
    days = _days(period)
    ae = AnalyticsEvent

    # Sessions, page_views, clicks in one query
    row = (
        await db.execute(
            select(
                func.count(distinct(ae.session_id)),
                func.count().filter(ae.event_type == "page_view"),
                func.count().filter(ae.event_type == "headline_click"),
            ).where(ae.created_at >= cutoff)
        )
    ).one()
    sessions, page_views, headline_clicks = row[0], row[1], row[2]
    ctr = round(headline_clicks / page_views, 4) if page_views > 0 else 0.0

    # Returning sessions: sessions that also have events before the cutoff
    returning_result = await db.execute(
        select(func.count(distinct(ae.session_id))).where(
            ae.created_at >= cutoff,
            ae.session_id.in_(
                select(ae.session_id).where(ae.created_at < cutoff).distinct()
            ),
        )
    )
    returning_sessions = returning_result.scalar() or 0
    new_sessions = sessions - returning_sessions

    return OverviewResponse(
        period_days=days,
        sessions=sessions,
        page_views=page_views,
        headline_clicks=headline_clicks,
        ctr=ctr,
        new_sessions=new_sessions,
        returning_sessions=returning_sessions,
    )


@router.get("/analytics/top-headlines", response_model=TopHeadlinesResponse)
async def analytics_top_headlines(
    db: AsyncSession = Depends(get_db),
    period: Period = Query(Period.seven_days),
    limit: int = Query(20, ge=1, le=100),
):
    cutoff = _cutoff(period)
    days = _days(period)

    result = await db.execute(
        select(
            AnalyticsEvent.article_id,
            Article.title,
            Source.name.label("source_name"),
            func.count().label("clicks"),
        )
        .join(Article, AnalyticsEvent.article_id == Article.id)
        .join(Source, Article.source_id == Source.id)
        .where(
            AnalyticsEvent.event_type == "headline_click",
            AnalyticsEvent.created_at >= cutoff,
            AnalyticsEvent.article_id.isnot(None),
        )
        .group_by(AnalyticsEvent.article_id, Article.title, Source.name)
        .order_by(func.count().desc())
        .limit(limit)
    )

    headlines = [
        TopHeadlineItem(
            article_id=str(row.article_id),
            title=row.title,
            source_name=row.source_name,
            clicks=row.clicks,
        )
        for row in result.all()
    ]

    return TopHeadlinesResponse(period_days=days, headlines=headlines)


@router.get("/analytics/by-source", response_model=BySourceResponse)
async def analytics_by_source(
    db: AsyncSession = Depends(get_db),
    period: Period = Query(Period.seven_days),
):
    cutoff = _cutoff(period)
    days = _days(period)
    ae = AnalyticsEvent

    result = await db.execute(
        select(
            ae.source_slug,
            func.count().label("clicks"),
        )
        .where(
            ae.event_type == "headline_click",
            ae.created_at >= cutoff,
            ae.source_slug.isnot(None),
        )
        .group_by(ae.source_slug)
        .order_by(func.count().desc())
    )
    rows = result.all()
    total_clicks = sum(r.clicks for r in rows)

    # Resolve source slugs to names
    slugs = [r.source_slug for r in rows]
    source_names: dict[str, str] = {}
    if slugs:
        name_result = await db.execute(
            select(Source.slug, Source.name).where(Source.slug.in_(slugs))
        )
        source_names = {r.slug: r.name for r in name_result.all()}

    sources = [
        SourceMetric(
            source_slug=r.source_slug,
            source_name=source_names.get(r.source_slug),
            clicks=r.clicks,
            share=round(r.clicks / total_clicks, 4) if total_clicks > 0 else 0.0,
        )
        for r in rows
    ]

    return BySourceResponse(period_days=days, total_clicks=total_clicks, sources=sources)


@router.get("/analytics/by-category", response_model=ByCategoryResponse)
async def analytics_by_category(
    db: AsyncSession = Depends(get_db),
    period: Period = Query(Period.seven_days),
):
    cutoff = _cutoff(period)
    days = _days(period)
    ae = AnalyticsEvent

    # Page views by category
    pv_result = await db.execute(
        select(
            ae.category_slug,
            func.count().label("page_views"),
        )
        .where(
            ae.event_type == "page_view",
            ae.created_at >= cutoff,
            ae.category_slug.isnot(None),
        )
        .group_by(ae.category_slug)
    )
    pv_map = {r.category_slug: r.page_views for r in pv_result.all()}

    # Clicks by category
    click_result = await db.execute(
        select(
            ae.category_slug,
            func.count().label("clicks"),
        )
        .where(
            ae.event_type == "headline_click",
            ae.created_at >= cutoff,
            ae.category_slug.isnot(None),
        )
        .group_by(ae.category_slug)
    )
    click_map = {r.category_slug: r.clicks for r in click_result.all()}

    all_slugs = sorted(set(pv_map.keys()) | set(click_map.keys()))
    categories = []
    for slug in all_slugs:
        pv = pv_map.get(slug, 0)
        cl = click_map.get(slug, 0)
        categories.append(
            CategoryMetric(
                category_slug=slug,
                clicks=cl,
                page_views=pv,
                ctr=round(cl / pv, 4) if pv > 0 else 0.0,
            )
        )
    categories.sort(key=lambda c: c.page_views, reverse=True)

    return ByCategoryResponse(period_days=days, categories=categories)


@router.get("/analytics/by-hour", response_model=ByHourResponse)
async def analytics_by_hour(
    db: AsyncSession = Depends(get_db),
    period: Period = Query(Period.seven_days),
):
    cutoff = _cutoff(period)
    days = _days(period)
    ae = AnalyticsEvent

    # Page views by hour
    pv_result = await db.execute(
        select(
            extract("hour", ae.created_at).label("hour"),
            func.count().label("count"),
        )
        .where(ae.event_type == "page_view", ae.created_at >= cutoff)
        .group_by(text("1"))
    )
    pv_map = {int(r.hour): r.count for r in pv_result.all()}

    # Clicks by hour
    click_result = await db.execute(
        select(
            extract("hour", ae.created_at).label("hour"),
            func.count().label("count"),
        )
        .where(ae.event_type == "headline_click", ae.created_at >= cutoff)
        .group_by(text("1"))
    )
    click_map = {int(r.hour): r.count for r in click_result.all()}

    hours = [
        HourMetric(
            hour=h,
            page_views=pv_map.get(h, 0),
            clicks=click_map.get(h, 0),
        )
        for h in range(24)
    ]

    return ByHourResponse(period_days=days, hours=hours)
