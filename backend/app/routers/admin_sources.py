from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.admin import get_admin
from app.database import get_db
from app.models import Article, FetchLog, Source
from app.schemas.admin import (
    BatchRefreshResponse,
    FetchLogResponse,
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    TestFetchArticle,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-sources"],
    dependencies=[Depends(get_admin)],
)


@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Source).order_by(Source.surface, Source.name))
    return list(result.scalars().all())


@router.post("/sources", response_model=SourceResponse)
async def create_source(body: SourceCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Source).where(Source.slug == body.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Source slug already exists")

    source = Source(**body.model_dump())
    db.add(source)
    await db.flush()
    return source


@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: uuid.UUID, body: SourceUpdate, db: AsyncSession = Depends(get_db)
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(source, field, value)

    await db.flush()
    return source


@router.delete("/sources/{source_id}")
async def delete_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")

    count = await db.scalar(
        select(func.count(Article.id)).where(Article.source_id == source_id)
    )
    await db.delete(source)
    return {"deleted": source.name, "articles_removed": count}


@router.post("/sources/{source_id}/refresh")
async def refresh_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")

    from app.scraper.scraper import scrape

    fetch_result = await scrape(db, source, trigger="manual")

    if fetch_result.articles_new > 0:
        from app.classifier.classifier import classify_batch

        await classify_batch(db, source_ids=[source.id], trigger="manual")
        if fetch_result.new_article_ids:
            from app.dedup import dedup_batch

            await dedup_batch(db, fetch_result.new_article_ids, trigger="manual")

    return {
        "status": fetch_result.status,
        "articles_new": fetch_result.articles_new,
        "articles_updated": fetch_result.articles_updated,
        "duration_ms": fetch_result.duration_ms,
    }


@router.post("/sources/{source_id}/test-fetch", response_model=list[TestFetchArticle])
async def test_fetch_source(source_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")

    from app.scraper.scraper import scrape

    fetch_result = await scrape(db, source, trigger="test")

    if fetch_result.error:
        raise HTTPException(400, fetch_result.error)

    if not fetch_result.articles:
        return []

    return [
        TestFetchArticle(
            external_id=a.external_id,
            title=a.title,
            url=a.url,
            summary=a.summary,
            published_at=a.published_at,
        )
        for a in fetch_result.articles
    ]


@router.post("/refresh-all")
async def refresh_all(db: AsyncSession = Depends(get_db)):
    from app.workers.fetch_worker import start_batch_refresh

    result = await start_batch_refresh(db)

    if "error" in result:
        raise HTTPException(429, result["error"])

    return result


@router.get("/refresh-status/{batch_id}")
async def refresh_status(batch_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(FetchLog, Source.name)
        .join(Source, FetchLog.source_id == Source.id)
        .where(FetchLog.batch_id == batch_id)
        .order_by(FetchLog.started_at.desc())
    )
    rows = result.all()

    return {
        "batch_id": str(batch_id),
        "sources": [
            {
                "source_name": name,
                "status": log.status,
                "articles_new": log.articles_new,
                "articles_updated": log.articles_updated,
                "duration_ms": log.duration_ms,
                "error_message": log.error_message,
            }
            for log, name in rows
        ],
    }


@router.get("/sources/{source_id}/fetch-logs", response_model=list[FetchLogResponse])
async def source_fetch_logs(
    source_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    source = await db.get(Source, source_id)
    if not source:
        raise HTTPException(404, "Source not found")

    offset = (page - 1) * per_page
    result = await db.execute(
        select(FetchLog)
        .where(FetchLog.source_id == source_id)
        .order_by(FetchLog.started_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    return list(result.scalars().all())
