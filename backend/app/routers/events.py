from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AnalyticsEvent
from app.schemas.events import AnalyticsEventCreate

router = APIRouter(prefix="/api", tags=["events"])


@router.post("/events", status_code=204)
async def create_event(
    event: AnalyticsEventCreate,
    db: AsyncSession = Depends(get_db),
):
    db_event = AnalyticsEvent(
        event_type=event.event_type,
        article_id=event.article_id,
        category_slug=event.category_slug,
        source_slug=event.source_slug,
        surface=event.surface,
        session_id=event.session_id,
        referrer=event.referrer,
    )
    db.add(db_event)
    return Response(status_code=204)
