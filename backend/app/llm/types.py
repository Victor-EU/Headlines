from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ClassificationItem:
    article_id: str
    categories: list[dict]  # [{"slug": "tech", "confidence": 0.9}]
    interest_score: int = 3


@dataclass
class ClassificationResult:
    classifications: list[ClassificationItem] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


@dataclass
class GenerationResult:
    text: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


@dataclass
class DedupItem:
    is_duplicate: bool = False
    duplicate_of: str | None = None
    best_representative: str | None = None
    confidence: float = 0.0
    reasoning: str = ""


@dataclass
class DedupResult:
    result: DedupItem | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0


class ProviderConfigError(Exception):
    """Raised when a required API key is missing."""

    def __init__(self, provider: str, env_var: str):
        self.provider = provider
        self.env_var = env_var
        super().__init__(f"Missing API key for {provider}. Set the {env_var} environment variable.")
