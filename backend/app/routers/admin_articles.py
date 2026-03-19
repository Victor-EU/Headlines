from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.auth.admin import get_admin
from app.database import get_db
from app.models import Article, ArticleCategory, Category, Source
from app.schemas.admin import (
    ArticleAdminResponse,
    ArticleCategoryDetail,
    ArticleUpdate,
    BulkArticleAction,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-articles"],
    dependencies=[Depends(get_admin)],
)


@router.get("/articles")
async def list_articles(
    db: AsyncSession = Depends(get_db),
    q: str | None = Query(None),
    source_id: uuid.UUID | None = Query(None),
    category_slug: str | None = Query(None),
    surface: str | None = Query(None),
    classified: bool | None = Query(None),
    hidden: bool | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    query = (
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .options(
            joinedload(Article.source),
            selectinload(Article.article_categories).selectinload(
                ArticleCategory.category
            ),
        )
    )

    if q:
        query = query.where(Article.title.ilike(f"%{q}%"))
    if source_id:
        query = query.where(Article.source_id == source_id)
    if surface:
        query = query.where(Source.surface == surface)
    if classified is not None:
        query = query.where(Article.classified == classified)
    if hidden is not None:
        query = query.where(Article.hidden == hidden)
    if category_slug:
        query = query.join(
            ArticleCategory, Article.id == ArticleCategory.article_id
        ).join(Category, ArticleCategory.category_id == Category.id).where(
            Category.slug == category_slug
        )

    # Count total
    count_q = (
        select(func.count(Article.id))
        .select_from(Article)
        .join(Source, Article.source_id == Source.id)
    )
    if q:
        count_q = count_q.where(Article.title.ilike(f"%{q}%"))
    if source_id:
        count_q = count_q.where(Article.source_id == source_id)
    if surface:
        count_q = count_q.where(Source.surface == surface)
    if classified is not None:
        count_q = count_q.where(Article.classified == classified)
    if hidden is not None:
        count_q = count_q.where(Article.hidden == hidden)
    if category_slug:
        count_q = count_q.join(
            ArticleCategory, Article.id == ArticleCategory.article_id
        ).join(Category, ArticleCategory.category_id == Category.id).where(
            Category.slug == category_slug
        )

    total = await db.scalar(count_q) or 0

    offset = (page - 1) * per_page
    query = query.order_by(Article.published_at.desc()).offset(offset).limit(per_page)

    result = await db.execute(query)
    articles = list(result.unique().scalars().all())

    items = []
    for article in articles:
        cats = [
            ArticleCategoryDetail(
                slug=ac.category.slug,
                confidence=ac.confidence,
                manual=ac.manual_override,
            )
            for ac in article.article_categories
        ]
        items.append(
            ArticleAdminResponse(
                id=article.id,
                title=article.title,
                url=article.url,
                source_name=article.source.name,
                published_at=article.published_at,
                classified=article.classified,
                hidden=article.hidden,
                is_representative=article.is_representative,
                categories=cats,
            )
        )

    return {
        "articles": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "has_next": (offset + per_page) < total,
        },
    }


@router.put("/articles/{article_id}")
async def update_article(
    article_id: uuid.UUID,
    body: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
):
    article = await db.get(Article, article_id)
    if not article:
        raise HTTPException(404, "Article not found")

    if body.hidden is not None:
        if body.hidden:
            from app.dedup.deduplicator import hide_article

            await hide_article(db, article_id)
        else:
            article.hidden = False

    if body.categories is not None:
        # Remove existing non-manual assignments
        existing_q = await db.execute(
            select(ArticleCategory).where(
                ArticleCategory.article_id == article_id,
                ArticleCategory.manual_override == False,
            )
        )
        for ac in existing_q.scalars().all():
            await db.delete(ac)

        # Add new manual assignments
        for cat_id in body.categories:
            cat = await db.get(Category, cat_id)
            if not cat:
                continue
            # Check if already manually assigned
            existing = await db.execute(
                select(ArticleCategory).where(
                    ArticleCategory.article_id == article_id,
                    ArticleCategory.category_id == cat_id,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(
                    ArticleCategory(
                        article_id=article_id,
                        category_id=cat_id,
                        confidence=1.0,
                        manual_override=True,
                    )
                )

    await db.flush()
    return {"updated": str(article_id)}


@router.post("/articles/bulk")
async def bulk_action(body: BulkArticleAction, db: AsyncSession = Depends(get_db)):
    if not body.article_ids:
        raise HTTPException(400, "No article IDs provided")

    if body.action == "hide":
        from app.dedup.deduplicator import hide_article

        for aid in body.article_ids:
            await hide_article(db, aid)
        return {"action": "hide", "affected": len(body.article_ids)}

    elif body.action == "unhide":
        for aid in body.article_ids:
            article = await db.get(Article, aid)
            if article:
                article.hidden = False
        return {"action": "unhide", "affected": len(body.article_ids)}

    elif body.action == "assign_category":
        if not body.category_id:
            raise HTTPException(400, "category_id required for assign_category")
        cat = await db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(404, "Category not found")

        added = 0
        for aid in body.article_ids:
            existing = await db.execute(
                select(ArticleCategory).where(
                    ArticleCategory.article_id == aid,
                    ArticleCategory.category_id == body.category_id,
                )
            )
            if not existing.scalar_one_or_none():
                db.add(
                    ArticleCategory(
                        article_id=aid,
                        category_id=body.category_id,
                        confidence=1.0,
                        manual_override=True,
                    )
                )
                added += 1
        return {"action": "assign_category", "added": added}

    else:
        raise HTTPException(400, f"Unknown action: {body.action}")
