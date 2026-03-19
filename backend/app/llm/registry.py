from __future__ import annotations

import asyncio
import logging
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import LLMModel, PipelineTask

from .anthropic import classify_anthropic, dedup_anthropic, generate_anthropic
from .google import classify_google, dedup_google, generate_google
from .openai import classify_openai, dedup_openai, generate_openai
from .types import (
    ClassificationResult,
    DedupResult,
    GenerationResult,
    ProviderConfigError,
)

logger = logging.getLogger(__name__)


class ProviderAdapter(NamedTuple):
    classify: callable
    dedup: callable
    generate: callable
    api_key_env: str


PROVIDERS: dict[str, ProviderAdapter] = {
    "anthropic": ProviderAdapter(classify_anthropic, dedup_anthropic, generate_anthropic, "ANTHROPIC_API_KEY"),
    "openai": ProviderAdapter(classify_openai, dedup_openai, generate_openai, "OPENAI_API_KEY"),
    "google": ProviderAdapter(classify_google, dedup_google, generate_google, "GOOGLE_AI_API_KEY"),
}


def get_api_key(provider: str) -> str:
    adapter = PROVIDERS.get(provider)
    if not adapter:
        raise ProviderConfigError(provider, f"Unknown provider: {provider}")

    key = getattr(settings, adapter.api_key_env, "")
    if not key:
        raise ProviderConfigError(provider, adapter.api_key_env)
    return key


async def run_classify(
    db: AsyncSession,
    task_name: str,
    system_prompt: str,
    user_prompt: str,
    tool_schema: dict,
) -> ClassificationResult:
    task, model = await _resolve_task_model(db, task_name)
    api_key = get_api_key(model.provider)
    adapter = PROVIDERS[model.provider]
    config = {**model.config, **task.config}

    # Retry once on failure
    for attempt in range(2):
        try:
            return await adapter.classify(
                api_key, model.model_id, system_prompt, user_prompt, tool_schema, config
            )
        except Exception as e:
            if attempt == 0:
                logger.warning(f"Classify attempt 1 failed for {task_name}: {e}, retrying...")
                await asyncio.sleep(2)
            else:
                raise


async def run_dedup(
    db: AsyncSession,
    task_name: str,
    system_prompt: str,
    user_prompt: str,
    tool_schema: dict,
) -> DedupResult:
    task, model = await _resolve_task_model(db, task_name)
    api_key = get_api_key(model.provider)
    adapter = PROVIDERS[model.provider]
    config = {**model.config, **task.config}

    for attempt in range(2):
        try:
            return await adapter.dedup(
                api_key, model.model_id, system_prompt, user_prompt, tool_schema, config
            )
        except Exception as e:
            if attempt == 0:
                logger.warning(f"Dedup attempt 1 failed: {e}, retrying...")
                await asyncio.sleep(2)
            else:
                raise


async def run_generate(
    db: AsyncSession,
    task_name: str,
    system_prompt: str,
    user_prompt: str,
) -> GenerationResult:
    task, model = await _resolve_task_model(db, task_name)
    api_key = get_api_key(model.provider)
    adapter = PROVIDERS[model.provider]
    config = {**model.config, **task.config}

    for attempt in range(2):
        try:
            return await adapter.generate(
                api_key, model.model_id, system_prompt, user_prompt, config
            )
        except Exception as e:
            if attempt == 0:
                logger.warning(f"Generate attempt 1 failed for {task_name}: {e}, retrying...")
                await asyncio.sleep(2)
            else:
                raise


async def _resolve_task_model(db: AsyncSession, task_name: str) -> tuple[PipelineTask, LLMModel]:
    task = await db.get(PipelineTask, task_name)
    if not task:
        raise ValueError(f"Pipeline task '{task_name}' not found")

    result = await db.execute(
        select(LLMModel).where(LLMModel.model_id == task.model_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise ValueError(f"LLM model '{task.model_id}' not found for task '{task_name}'")

    return task, model
