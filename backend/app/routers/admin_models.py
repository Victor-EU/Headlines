from __future__ import annotations

import os
import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.admin import get_admin
from app.database import get_db
from app.models import LLMModel, PipelineTask
from app.schemas.admin import LLMModelCreate, LLMModelResponse, LLMModelUpdate

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-models"],
    dependencies=[Depends(get_admin)],
)


@router.get("/models", response_model=list[LLMModelResponse])
async def list_models(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LLMModel).order_by(LLMModel.provider, LLMModel.model_id))
    return list(result.scalars().all())


@router.post("/models", response_model=LLMModelResponse)
async def create_model(body: LLMModelCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(LLMModel).where(LLMModel.model_id == body.model_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, f"Model '{body.model_id}' already exists")

    model = LLMModel(**body.model_dump())
    db.add(model)
    await db.flush()
    return model


@router.put("/models/{model_id}", response_model=LLMModelResponse)
async def update_model(
    model_id: str, body: LLMModelUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Model not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(model, field, value)

    await db.flush()
    return model


@router.delete("/models/{model_id}")
async def delete_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Model not found")

    # Check if any active task uses this model
    task_using = await db.execute(
        select(PipelineTask).where(
            PipelineTask.model_id == model_id, PipelineTask.active == True
        )
    )
    if task_using.scalar_one_or_none():
        raise HTTPException(409, "Model is assigned to an active pipeline task")

    await db.delete(model)
    return {"deleted": model.model_id}


@router.post("/models/{model_id}/test")
async def test_model(model_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(404, "Model not found")

    from app.classifier.prompts import (
        CLASSIFICATION_SYSTEM_PROMPT,
        CLASSIFICATION_TOOL_SCHEMA,
        build_classification_prompt,
    )
    from app.llm.registry import PROVIDERS, get_api_key
    from app.models import Article, Category, Source

    # Load 3 recent news articles
    articles_q = await db.execute(
        select(Article)
        .join(Source, Article.source_id == Source.id)
        .where(Source.surface == "news", Article.classified == True)
        .order_by(Article.published_at.desc())
        .limit(3)
    )
    articles = list(articles_q.scalars().all())

    if not articles:
        raise HTTPException(400, "No articles available for testing")

    # Load news categories
    cat_q = await db.execute(
        select(Category).where(Category.surface == "news", Category.active == True)
    )
    categories = list(cat_q.scalars().all())
    cat_list = [{"slug": c.slug, "description": c.description} for c in categories]

    article_data = [
        {"id": str(a.id), "title": a.title, "summary": a.summary} for a in articles
    ]

    user_prompt = build_classification_prompt(article_data, cat_list)

    try:
        api_key = get_api_key(model.provider)
    except Exception as e:
        raise HTTPException(400, f"API key not configured: {e}")

    adapter = PROVIDERS[model.provider]
    start = time.monotonic()
    try:
        llm_result = await adapter.classify(
            api_key,
            model.model_id,
            CLASSIFICATION_SYSTEM_PROMPT,
            user_prompt,
            CLASSIFICATION_TOOL_SCHEMA,
            model.config or {},
        )
        latency_ms = int((time.monotonic() - start) * 1000)

        return {
            "success": True,
            "latency_ms": latency_ms,
            "input_tokens": llm_result.input_tokens,
            "output_tokens": llm_result.output_tokens,
            "result_preview": [
                {"article_id": c.article_id, "categories": c.categories}
                for c in llm_result.classifications[:3]
            ],
        }
    except Exception as e:
        latency_ms = int((time.monotonic() - start) * 1000)
        return {
            "success": False,
            "latency_ms": latency_ms,
            "error": str(e),
        }


@router.get("/models/providers")
async def provider_status():
    providers = [
        {"provider": "anthropic", "env_var": "ANTHROPIC_API_KEY"},
        {"provider": "openai", "env_var": "OPENAI_API_KEY"},
        {"provider": "google", "env_var": "GOOGLE_AI_API_KEY"},
    ]
    result = []
    for p in providers:
        key = os.environ.get(p["env_var"], "")
        result.append(
            {
                "provider": p["provider"],
                "key_configured": bool(key),
                "key_masked": f"****{key[-4:]}" if len(key) > 4 else "",
            }
        )
    return result
