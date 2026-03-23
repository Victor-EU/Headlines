from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.database import get_db
from app.models import Article, ArticleCategory, Category, CategoryRedirect, Source
from app.schemas.common import PaginationMeta
from app.schemas.headlines import AlsoReportedBy, HeadlineItem, HeadlinesResponse

router = APIRouter(prefix="/api", tags=["headlines"])


@router.get("/headlines")
async def get_headlines(
    response: Response,
    db: AsyncSession = Depends(get_db),
    surface: str = Query("news"),
    category: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
):
    # Category slug redirect check
    if category:
        cat_exists = await db.execute(
            select(Category).where(Category.slug == category, Category.active == True)
        )
        if not cat_exists.scalar_one_or_none():
            redirect = await db.execute(
                select(CategoryRedirect).where(
                    CategoryRedirect.old_slug == category,
                    CategoryRedirect.surface == surface,
                )
            )
            redir = redirect.scalar_one_or_none()
            if redir:
                base_path = "/learning" if surface == "learning" else ""
                return RedirectResponse(
                    url=f"{base_path}/{redir.new_slug}",
                    status_code=301,
                )
            return JSONResponse(status_code=404, content={"detail": "Category not found"})

    # Build query
    q = (
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .options(joinedload(Article.source), selectinload(Article.article_categories).selectinload(ArticleCategory.category))
        .where(
            Source.surface == surface,
            Article.hidden == False,
            Article.classified == True,
            Article.is_representative == True,
        )
    )

    if category:
        q = q.join(ArticleCategory, Article.id == ArticleCategory.article_id).join(
            Category, ArticleCategory.category_id == Category.id
        ).where(Category.slug == category)

    # Count total
    count_q = (
        select(func.count(Article.id))
        .select_from(Article)
        .join(Source, Article.source_id == Source.id)
        .where(
            Source.surface == surface,
            Article.hidden == False,
            Article.classified == True,
            Article.is_representative == True,
        )
    )
    if category:
        count_q = count_q.join(ArticleCategory, Article.id == ArticleCategory.article_id).join(
            Category, ArticleCategory.category_id == Category.id
        ).where(Category.slug == category)

    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    # Paginate
    offset = (page - 1) * per_page
    q = q.order_by(
        Article.interest_score.desc().nulls_last(),
        Article.published_at.desc(),
    ).offset(offset).limit(per_page)

    result = await db.execute(q)
    articles = list(result.unique().scalars().all())

    # Collect cluster_ids for also_reported_by
    cluster_ids = {a.cluster_id for a in articles if a.cluster_id}
    cluster_articles: dict[uuid.UUID, list[Article]] = {}

    if cluster_ids:
        cluster_q = await db.execute(
            select(Article)
            .options(joinedload(Article.source))
            .where(
                Article.cluster_id.in_(cluster_ids),
                Article.hidden == False,
            )
        )
        for ca in cluster_q.unique().scalars().all():
            cluster_articles.setdefault(ca.cluster_id, []).append(ca)

    # Build response
    headlines = []
    for article in articles:
        cats = [ac.category.slug for ac in article.article_categories]

        also = []
        if article.cluster_id and article.cluster_id in cluster_articles:
            for ca in cluster_articles[article.cluster_id]:
                if ca.id != article.id:
                    also.append(AlsoReportedBy(
                        source_name=ca.source.name,
                        source_slug=ca.source.slug,
                        url=ca.url,
                    ))

        headlines.append(HeadlineItem(
            id=article.id,
            title=article.title,
            url=article.url,
            summary=article.summary if surface == "learning" else None,
            source_name=article.source.name,
            source_slug=article.source.slug,
            source_homepage=article.source.homepage_url,
            published_at=article.published_at,
            categories=cats,
            also_reported_by=also,
            interest_score=article.interest_score,
        ))

    # Cache headers
    cache_seconds = 120 if surface == "news" else 1800
    response.headers["Cache-Control"] = f"public, max-age={cache_seconds}"

    return HeadlinesResponse(
        surface=surface,
        headlines=headlines,
        pagination=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            has_next=(offset + per_page) < total,
        ),
    )
