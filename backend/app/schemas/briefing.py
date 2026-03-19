from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class BriefingResponse(BaseModel):
    type: str
    date: date
    brief: str | None = None
    generated_at: datetime | None = None
    focus_topic: str | None = None
    focus_body: str | None = None
