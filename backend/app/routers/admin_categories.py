from __future__ import annotations

import asyncio
import re
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.auth.admin import get_admin
from app.database import async_session, get_db
from app.models import (
    Article,
    ArticleCategory,
    Category,
    CategoryRedirect,
    Source,
)
from app.schemas.admin import (
    CategoryAdminResponse,
    CategoryCreate,
    CategoryUpdate,
    MergeRequest,
    PreviewRequest,
    PreviewResult,
    ReclassifyProgress,
    ReclassifyRequest,
    ReorderItem,
)

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-categories"],
    dependencies=[Depends(get_admin)],
)

_reclassify_jobs: dict[str, dict] = {}


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug.strip("-")


@router.get("/categories", response_model=list[CategoryAdminResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Get categories with 7-day article counts
    result = await db.execute(
        select(
            Category,
            func.count(ArticleCategory.article_id).label("article_count"),
        )
        .outerjoin(
            ArticleCategory,
            (ArticleCategory.category_id == Category.id)
            & (ArticleCategory.created_at >= seven_days_ago),
        )
        .group_by(Category.id)
        .order_by(Category.surface, Category.display_order)
    )

    categories = []
    for cat, count in result.all():
        resp = CategoryAdminResponse.model_validate(cat)
        resp.article_count = count
        categories.append(resp)

    return categories


@router.post("/categories", response_model=CategoryAdminResponse)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    slug = slugify(body.name)
    existing = await db.execute(select(Category).where(Category.slug == slug, Category.surface == body.surface))
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Category slug '{slug}' already exists")

    # Get max display_order for surface
    max_order = await db.scalar(
        select(func.max(Category.display_order)).where(
            Category.surface == body.surface
        )
    )
    display_order = (max_order or 0) + 1

    category = Category(
        name=body.name,
        slug=slug,
        surface=body.surface,
        description=body.description,
        display_order=display_order,
    )
    db.add(category)
    await db.flush()

    resp = CategoryAdminResponse.model_validate(category)
    resp.article_count = 0
    return resp


# CRITICAL: /reorder MUST be before /{id} to avoid route conflict
@router.put("/categories/reorder")
async def reorder_categories(
    items: list[ReorderItem], db: AsyncSession = Depends(get_db)
):
    for item in items:
        await db.execute(
            update(Category)
            .where(Category.id == item.id)
            .values(display_order=item.display_order)
        )
    return {"reordered": len(items)}


@router.put("/categories/{category_id}", response_model=CategoryAdminResponse)
async def update_category(
    category_id: uuid.UUID,
    body: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")

    updates = body.model_dump(exclude_unset=True)

    # Handle slug change → redirect with chain collapse
    if "slug" in updates and updates["slug"] and updates["slug"] != category.slug:
        new_slug = updates["slug"]

        # Check slug uniqueness
        existing = await db.execute(
            select(Category).where(Category.slug == new_slug, Category.surface == category.surface, Category.id != category_id)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(400, f"Category slug '{new_slug}' already exists")

        old_slug = category.slug

        # Collapse existing chains pointing to old_slug
        await db.execute(
            update(CategoryRedirect)
            .where(
                CategoryRedirect.new_slug == old_slug,
                CategoryRedirect.surface == category.surface,
            )
            .values(new_slug=new_slug)
        )

        # Create new redirect
        db.add(
            CategoryRedirect(
                old_slug=old_slug,
                new_slug=new_slug,
                surface=category.surface,
            )
        )

    for field, value in updates.items():
        setattr(category, field, value)

    await db.flush()

    resp = CategoryAdminResponse.model_validate(category)
    return resp


@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")

    count = await db.scalar(
        select(func.count(ArticleCategory.article_id)).where(
            ArticleCategory.category_id == category_id
        )
    )
    await db.delete(category)
    return {"deleted": category.name, "articles_affected": count}


@router.post("/categories/{category_id}/preview", response_model=PreviewResult)
async def preview_category(
    category_id: uuid.UUID,
    body: PreviewRequest,
    db: AsyncSession = Depends(get_db),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(404, "Category not found")

    # Load all active categories for this surface
    cat_result = await db.execute(
        select(Category).where(
            Category.surface == category.surface, Category.active == True
        )
    )
    categories = list(cat_result.scalars().all())
    cat_list = []
    for c in categories:
        desc = c.description
        if c.id == category_id and body.description is not None:
            desc = body.description
        cat_list.append({"slug": c.slug, "description": desc})

    # Load last 50 classified articles from the surface
    article_q = await db.execute(
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .options(joinedload(Article.source))
        .where(
            Source.surface == category.surface,
            Article.classified == True,
        )
        .order_by(Article.published_at.desc())
        .limit(50)
    )
    articles = list(article_q.unique().scalars().all())

    if not articles:
        return PreviewResult(would_match=[], currently_matched=[])

    article_data = [
        {"id": str(a.id), "title": a.title, "summary": a.summary} for a in articles
    ]

    from app.classifier.prompts import (
        CLASSIFICATION_SYSTEM_PROMPT,
        CLASSIFICATION_TOOL_SCHEMA,
        build_classification_prompt,
    )
    from app.llm.registry import run_classify

    user_prompt = build_classification_prompt(article_data, cat_list)
    llm_result = await run_classify(
        db,
        "classification",
        CLASSIFICATION_SYSTEM_PROMPT,
        user_prompt,
        CLASSIFICATION_TOOL_SCHEMA,
    )

    # Parse would_match
    would_match = []
    result_map = {c.article_id: c.categories for c in llm_result.classifications}
    for article in articles:
        aid = str(article.id)
        cats = result_map.get(aid, [])
        for cat in cats:
            if cat.get("slug") == category.slug and cat.get("confidence", 0) >= 0.5:
                would_match.append(
                    {
                        "article_id": aid,
                        "title": article.title,
                        "confidence": cat["confidence"],
                    }
                )
                break

    # Load current article_categories for these articles
    article_ids = [a.id for a in articles]
    current_q = await db.execute(
        select(ArticleCategory)
        .options(selectinload(ArticleCategory.article))
        .where(
            ArticleCategory.category_id == category_id,
            ArticleCategory.article_id.in_(article_ids),
        )
    )
    current_acs = list(current_q.scalars().all())

    currently_matched = [
        {
            "article_id": str(ac.article_id),
            "title": ac.article.title,
            "confidence": ac.confidence,
        }
        for ac in current_acs
    ]

    return PreviewResult(would_match=would_match, currently_matched=currently_matched)


@router.post("/categories/{category_id}/merge")
async def merge_categories(
    category_id: uuid.UUID,
    body: MergeRequest,
    db: AsyncSession = Depends(get_db),
):
    if category_id == body.target_id:
        raise HTTPException(400, "Cannot merge a category into itself")

    source_category = await db.get(Category, category_id)
    if not source_category:
        raise HTTPException(404, "Source category not found")

    target_category = await db.get(Category, body.target_id)
    if not target_category:
        raise HTTPException(404, "Target category not found")

    # Reassign article_categories (skip duplicates)
    existing_subq = select(ArticleCategory.article_id).where(
        ArticleCategory.category_id == body.target_id
    )
    await db.execute(
        update(ArticleCategory)
        .where(
            ArticleCategory.category_id == category_id,
            ~ArticleCategory.article_id.in_(existing_subq),
        )
        .values(category_id=body.target_id)
    )

    # Delete remaining duplicates
    await db.execute(
        delete(ArticleCategory).where(ArticleCategory.category_id == category_id)
    )

    # Create redirect
    db.add(
        CategoryRedirect(
            old_slug=source_category.slug,
            new_slug=target_category.slug,
            surface=source_category.surface,
        )
    )

    # Delete source category
    await db.delete(source_category)

    return {
        "merged": source_category.name,
        "into": target_category.name,
    }


@router.post("/reclassify")
async def start_reclassify(body: ReclassifyRequest, db: AsyncSession = Depends(get_db)):
    # Count affected articles to report immediately
    if body.since == "24h":
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    q = select(func.count(Article.id)).join(Source).where(Article.fetched_at >= cutoff)
    if body.surface:
        q = q.where(Source.surface == body.surface)
    total = await db.scalar(q) or 0

    job_id = str(uuid.uuid4())
    _reclassify_jobs[job_id] = {"total": total, "processed": 0, "status": "starting"}
    asyncio.create_task(_run_reclassify(job_id, body.since, body.surface))
    return {"job_id": job_id, "total": total}


@router.get("/reclassify/{job_id}", response_model=ReclassifyProgress)
async def reclassify_progress(job_id: str):
    job = _reclassify_jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return ReclassifyProgress(job_id=job_id, **job)


async def _run_reclassify(job_id: str, since: str, surface: str | None):
    try:
        async with async_session() as db:
            if since == "24h":
                cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            else:
                cutoff = datetime.now(timezone.utc) - timedelta(days=7)

            q = select(Article).join(Source).where(Article.fetched_at >= cutoff)
            if surface:
                q = q.where(Source.surface == surface)
            result = await db.execute(q)
            articles = list(result.scalars().all())

            total = len(articles)
            _reclassify_jobs[job_id] = {
                "total": total,
                "processed": 0,
                "status": "running",
            }

            if not articles:
                _reclassify_jobs[job_id] = {
                    "total": 0,
                    "processed": 0,
                    "status": "complete",
                }
                return

            article_ids = [a.id for a in articles]

            # Clear non-manual classifications
            await db.execute(
                delete(ArticleCategory).where(
                    ArticleCategory.article_id.in_(article_ids),
                    ArticleCategory.manual_override == False,
                )
            )
            await db.execute(
                update(Article)
                .where(Article.id.in_(article_ids))
                .values(classified=False, classification_attempts=0)
            )
            await db.flush()

            # Run classification
            from app.classifier.classifier import classify_batch

            await classify_batch(db, trigger="reclassify")
            await db.commit()

            _reclassify_jobs[job_id] = {
                "total": total,
                "processed": total,
                "status": "complete",
            }
    except Exception as e:
        _reclassify_jobs[job_id] = {
            "total": _reclassify_jobs.get(job_id, {}).get("total", 0),
            "processed": 0,
            "status": f"failed: {e}",
        }
