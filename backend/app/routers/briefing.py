from __future__ import annotations

from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Briefing
from app.schemas.briefing import BriefingResponse

router = APIRouter(prefix="/api", tags=["briefing"])


@router.get("/briefing", response_model=BriefingResponse)
async def get_briefing(
    response: Response,
    db: AsyncSession = Depends(get_db),
    type: str = Query("daily_news"),
    date_str: str | None = Query(None, alias="date"),
):
    if date_str:
        briefing_date = date.fromisoformat(date_str)
    elif type == "weekly_learning":
        # Default to current week's Monday
        today = date.today()
        briefing_date = today - __import__("datetime").timedelta(days=today.weekday())
    else:
        briefing_date = date.today()

    result = await db.execute(
        select(Briefing).where(Briefing.type == type, Briefing.date == briefing_date)
    )
    briefing = result.scalar_one_or_none()

    if briefing:
        cache_seconds = 1800 if type == "weekly_learning" else 300
        response.headers["Cache-Control"] = f"public, max-age={cache_seconds}"
        return BriefingResponse(
            type=briefing.type,
            date=briefing.date,
            brief=briefing.brief,
            generated_at=briefing.generated_at,
            focus_topic=briefing.focus_topic,
            focus_body=briefing.focus_body,
        )

    response.headers["Cache-Control"] = "public, max-age=60"
    return BriefingResponse(type=type, date=briefing_date, brief=None)
