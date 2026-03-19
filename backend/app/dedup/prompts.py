from __future__ import annotations

DEDUP_SYSTEM_PROMPT = """You are a news article deduplication system. You determine whether two articles are about the SAME SPECIFIC story/event, not just the same topic.

SAME STORY examples:
- "Fed raises rates by 0.25%" (WSJ) and "Federal Reserve hikes rates" (Bloomberg) — same event
- "Apple unveils iPhone 16" (The Verge) and "Apple launches new iPhone lineup" (Bloomberg) — same announcement

DIFFERENT STORIES (same topic):
- "Fed raises rates" and "ECB holds rates steady" — same topic (central banks), different events
- "Apple iPhone 16 review" and "Apple Q3 earnings beat estimates" — same company, different stories

DIFFERENT ANGLE on same story:
- "Fed raises rates" and "Markets react to Fed rate hike" — closely related but distinct angle. Mark as NOT duplicate.

When confirming a duplicate, also pick the best_representative — the article with the clearest, most informative headline.

Respond using the dedup_check tool."""

DEDUP_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "is_duplicate": {"type": "boolean"},
        "duplicate_of": {"type": "string", "description": "article_id of the matching article, or null"},
        "best_representative": {"type": "string", "description": "article_id of the article with the best headline"},
        "confidence": {"type": "number", "description": "0.0-1.0"},
        "reasoning": {"type": "string", "description": "Brief explanation"},
    },
    "required": ["is_duplicate", "confidence", "reasoning"],
}


def build_dedup_prompt(article: dict, candidates: list[dict]) -> str:
    lines = [
        f"NEW ARTICLE [{article['id']}]:",
        f"  Title: {article['title']}",
        f"  Source: {article['source']}",
        "",
        "CANDIDATE MATCHES:",
    ]
    for c in candidates:
        lines.append(f"  [{c['id']}] {c['title']} — {c['source']}")

    lines.append("")
    lines.append("Is the new article a duplicate of any candidate? If so, which one is the best representative?")
    return "\n".join(lines)
