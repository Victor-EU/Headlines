import json
import logging
import re
import time

from google import genai

from .types import ClassificationItem, ClassificationResult, DedupItem, DedupResult, GenerationResult

logger = logging.getLogger(__name__)

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def _strip_fences(text: str) -> str:
    match = _FENCE_RE.search(text)
    return match.group(1) if match else text


async def classify_google(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> ClassificationResult:
    client = genai.Client(api_key=api_key)
    start = time.monotonic()

    generation_config = {
        "response_mime_type": "application/json",
    }
    if config.get("thinkingBudget"):
        generation_config["thinking_config"] = {"thinking_budget": config["thinkingBudget"]}

    response = await client.aio.models.generate_content(
        model=model_id,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config=generation_config,
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    text = response.text or "{}"
    text = _strip_fences(text)
    data = json.loads(text)

    classifications = []
    for item in data.get("articles", []):
        classifications.append(
            ClassificationItem(
                article_id=item.get("article_id", ""),
                categories=item.get("categories", []),
            )
        )

    input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

    return ClassificationResult(
        classifications=classifications,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )


async def dedup_google(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, tool_schema: dict, config: dict
) -> DedupResult:
    client = genai.Client(api_key=api_key)
    start = time.monotonic()

    response = await client.aio.models.generate_content(
        model=model_id,
        contents=f"{system_prompt}\n\n{user_prompt}",
        config={"response_mime_type": "application/json"},
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    text = _strip_fences(response.text or "{}")
    data = json.loads(text)

    result = DedupItem(
        is_duplicate=data.get("is_duplicate", False),
        duplicate_of=data.get("duplicate_of"),
        best_representative=data.get("best_representative"),
        confidence=data.get("confidence", 0.0),
        reasoning=data.get("reasoning", ""),
    )

    input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

    return DedupResult(
        result=result,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )


async def generate_google(
    api_key: str, model_id: str, system_prompt: str, user_prompt: str, config: dict
) -> GenerationResult:
    client = genai.Client(api_key=api_key)
    start = time.monotonic()

    response = await client.aio.models.generate_content(
        model=model_id,
        contents=f"{system_prompt}\n\n{user_prompt}",
    )

    latency_ms = int((time.monotonic() - start) * 1000)

    input_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
    output_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0

    return GenerationResult(
        text=(response.text or "").strip(),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )
