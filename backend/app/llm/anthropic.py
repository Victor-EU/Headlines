import json
import logging
import time

from anthropic import AsyncAnthropic

from .types import ClassificationResult, ClassificationItem, DedupItem, DedupResult, GenerationResult

logger = logging.getLogger(__name__)


async def classify_anthropic(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> ClassificationResult:
    client = AsyncAnthropic(api_key=api_key)
    start = time.monotonic()

    response = await client.messages.create(
        model=model_id,
        max_tokens=config.get("max_tokens", 4096),
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[
            {
                "name": "classify_articles",
                "description": "Classify the provided articles into categories.",
                "input_schema": tool_schema,
            }
        ],
        tool_choice={"type": "tool", "name": "classify_articles"},
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    # Extract tool_use block — model may add text blocks alongside
    tool_input = None
    for block in response.content:
        if block.type == "tool_use":
            tool_input = block.input
            break

    classifications = []
    if tool_input and "articles" in tool_input:
        for item in tool_input["articles"]:
            classifications.append(
                ClassificationItem(
                    article_id=item.get("article_id", ""),
                    categories=item.get("categories", []),
                )
            )

    return ClassificationResult(
        classifications=classifications,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=latency_ms,
    )


async def dedup_anthropic(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> DedupResult:
    client = AsyncAnthropic(api_key=api_key)
    start = time.monotonic()

    response = await client.messages.create(
        model=model_id,
        max_tokens=config.get("max_tokens", 1024),
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
        tools=[
            {
                "name": "dedup_check",
                "description": "Determine if two articles are about the same story.",
                "input_schema": tool_schema,
            }
        ],
        tool_choice={"type": "tool", "name": "dedup_check"},
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    tool_input = None
    for block in response.content:
        if block.type == "tool_use":
            tool_input = block.input
            break

    result = None
    if tool_input:
        result = DedupItem(
            is_duplicate=tool_input.get("is_duplicate", False),
            duplicate_of=tool_input.get("duplicate_of"),
            best_representative=tool_input.get("best_representative"),
            confidence=tool_input.get("confidence", 0.0),
            reasoning=tool_input.get("reasoning", ""),
        )

    return DedupResult(
        result=result,
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=latency_ms,
    )


async def generate_anthropic(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, config: dict
) -> GenerationResult:
    client = AsyncAnthropic(api_key=api_key)
    start = time.monotonic()

    response = await client.messages.create(
        model=model_id,
        max_tokens=config.get("max_tokens", 2048),
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    text = ""
    for block in response.content:
        if block.type == "text":
            text += block.text

    return GenerationResult(
        text=text.strip(),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
        latency_ms=latency_ms,
    )
