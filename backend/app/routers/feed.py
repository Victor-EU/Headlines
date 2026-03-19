from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import timezone
from email.utils import format_datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.database import get_db
from app.models import Article, Source

router = APIRouter(prefix="/api", tags=["feed"])


@router.get("/feed.xml")
async def rss_feed(
    db: AsyncSession = Depends(get_db),
    surface: str = Query("news"),
):
    q = (
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .options(joinedload(Article.source))
        .where(
            Source.surface == surface,
            Article.hidden == False,
            Article.classified == True,
            Article.is_representative == True,
        )
        .order_by(Article.published_at.desc())
        .limit(50)
    )
    result = await db.execute(q)
    articles = list(result.unique().scalars().all())

    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = f"Headlines — {surface.title()}"
    ET.SubElement(channel, "link").text = "https://headlines.example.com"
    ET.SubElement(channel, "description").text = f"Curated {surface} headlines"

    if articles:
        pub_at = articles[0].published_at
        if pub_at.tzinfo is None:
            pub_at = pub_at.replace(tzinfo=timezone.utc)
        ET.SubElement(channel, "lastBuildDate").text = format_datetime(pub_at)

    for article in articles:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = article.url
        ET.SubElement(item, "guid", isPermaLink="true").text = article.url
        if article.summary:
            ET.SubElement(item, "description").text = article.summary
        pub = article.published_at
        if pub.tzinfo is None:
            pub = pub.replace(tzinfo=timezone.utc)
        ET.SubElement(item, "pubDate").text = format_datetime(pub)
        source_el = ET.SubElement(item, "source", url=article.source.homepage_url)
        source_el.text = article.source.name

    xml_bytes = ET.tostring(rss, encoding="unicode", xml_declaration=False)
    xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_bytes

    return Response(
        content=xml_str,
        media_type="application/rss+xml; charset=utf-8",
        headers={"Cache-Control": "public, max-age=300"},
    )
