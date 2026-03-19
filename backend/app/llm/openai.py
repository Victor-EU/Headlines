import json
import logging
import time

from openai import AsyncOpenAI

from .types import ClassificationItem, ClassificationResult, DedupItem, DedupResult, GenerationResult

logger = logging.getLogger(__name__)


async def classify_openai(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> ClassificationResult:
    client = AsyncOpenAI(api_key=api_key)
    start = time.monotonic()

    response = await client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "classification",
                "schema": tool_schema,
                "strict": True,
            },
        },
        **({} if not config.get("reasoning_effort") else {"reasoning_effort": config["reasoning_effort"]}),
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)

    classifications = []
    for item in data.get("articles", []):
        classifications.append(
            ClassificationItem(
                article_id=item.get("article_id", ""),
                categories=item.get("categories", []),
            )
        )

    return ClassificationResult(
        classifications=classifications,
        input_tokens=response.usage.prompt_tokens if response.usage else 0,
        output_tokens=response.usage.completion_tokens if response.usage else 0,
        latency_ms=latency_ms,
    )


async def dedup_openai(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> DedupResult:
    client = AsyncOpenAI(api_key=api_key)
    start = time.monotonic()

    response = await client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "dedup_check",
                "schema": tool_schema,
                "strict": True,
            },
        },
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    content = response.choices[0].message.content or "{}"
    data = json.loads(content)

    result = DedupItem(
        is_duplicate=data.get("is_duplicate", False),
        duplicate_of=data.get("duplicate_of"),
        best_representative=data.get("best_representative"),
        confidence=data.get("confidence", 0.0),
        reasoning=data.get("reasoning", ""),
    )

    return DedupResult(
        result=result,
        input_tokens=response.usage.prompt_tokens if response.usage else 0,
        output_tokens=response.usage.completion_tokens if response.usage else 0,
        latency_ms=latency_ms,
    )


async def generate_openai(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, config: dict
) -> GenerationResult:
    client = AsyncOpenAI(api_key=api_key)
    start = time.monotonic()

    response = await client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    return GenerationResult(
        text=(response.choices[0].message.content or "").strip(),
        input_tokens=response.usage.prompt_tokens if response.usage else 0,
        output_tokens=response.usage.completion_tokens if response.usage else 0,
        latency_ms=latency_ms,
    )
