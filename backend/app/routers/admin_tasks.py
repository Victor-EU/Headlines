from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.admin import get_admin
from app.database import get_db
from app.models import LLMModel, PipelineLog, PipelineTask
from app.schemas.admin import PipelineTaskResponse, PipelineTaskUpdate

router = APIRouter(
    prefix="/api/admin",
    tags=["admin-tasks"],
    dependencies=[Depends(get_admin)],
)


@router.get("/tasks", response_model=list[PipelineTaskResponse])
async def list_tasks(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PipelineTask).order_by(PipelineTask.task))
    return list(result.scalars().all())


@router.put("/tasks/{task_name}", response_model=PipelineTaskResponse)
async def update_task(
    task_name: str,
    body: PipelineTaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    task = await db.get(PipelineTask, task_name)
    if not task:
        raise HTTPException(404, "Task not found")

    updates = body.model_dump(exclude_unset=True)

    # Validate model_id change
    if "model_id" in updates and updates["model_id"]:
        model_result = await db.execute(
            select(LLMModel).where(
                LLMModel.model_id == updates["model_id"], LLMModel.active == True
            )
        )
        model = model_result.scalar_one_or_none()
        if not model:
            raise HTTPException(400, "Model not found or inactive")

        # Check provider API key
        from app.llm.registry import PROVIDERS

        adapter = PROVIDERS.get(model.provider)
        if adapter:
            key = os.environ.get(adapter.api_key_env, "")
            if not key:
                raise HTTPException(
                    400, f"API key not configured for provider '{model.provider}'"
                )

    for field, value in updates.items():
        setattr(task, field, value)

    await db.flush()
    return task


@router.get("/tasks/cost-estimate")
async def cost_estimate(db: AsyncSession = Depends(get_db)):
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    task_names = ["classification", "dedup", "briefing", "learning_digest"]

    estimates = {}
    for task_name in task_names:
        result = await db.execute(
            select(
                func.sum(PipelineLog.input_tokens),
                func.sum(PipelineLog.output_tokens),
                func.sum(PipelineLog.estimated_cost_usd),
            ).where(
                PipelineLog.task == task_name, PipelineLog.started_at >= cutoff
            )
        )
        row = result.one()
        weekly_cost = row[2] or 0.0
        daily_cost = weekly_cost / 7
        monthly_cost = daily_cost * 30

        estimates[task_name] = {
            "weekly_input_tokens": row[0] or 0,
            "weekly_output_tokens": row[1] or 0,
            "weekly_cost_usd": round(weekly_cost, 4),
            "daily_cost_usd": round(daily_cost, 4),
            "monthly_cost_usd": round(monthly_cost, 4),
        }

    return estimates
