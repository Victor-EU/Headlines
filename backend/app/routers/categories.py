from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Article, ArticleCategory, Category, Source
from app.schemas.headlines import CategoryResponse

router = APIRouter(prefix="/api", tags=["categories"])


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    response: Response,
    db: AsyncSession = Depends(get_db),
    surface: str = Query("news"),
):
    # Article count window: 24h for news, 7d for learning
    if surface == "learning":
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    # Get categories with article counts
    q = (
        select(
            Category,
            func.count(ArticleCategory.article_id).label("article_count"),
        )
        .outerjoin(ArticleCategory, Category.id == ArticleCategory.category_id)
        .outerjoin(
            Article,
            (ArticleCategory.article_id == Article.id)
            & (Article.published_at >= cutoff)
            & (Article.hidden == False)
            & (Article.is_representative == True),
        )
        .where(Category.surface == surface, Category.active == True)
        .group_by(Category.id)
        .order_by(Category.display_order.asc())
    )

    result = await db.execute(q)
    rows = result.all()

    categories = []
    for cat, count in rows:
        categories.append(CategoryResponse(
            name=cat.name,
            slug=cat.slug,
            article_count=count or 0,
        ))

    response.headers["Cache-Control"] = "public, max-age=600"
    return categories
