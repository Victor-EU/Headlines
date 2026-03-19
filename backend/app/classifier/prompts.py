from __future__ import annotations

CLASSIFICATION_SYSTEM_PROMPT = """You are a news article classifier. You assign articles to categories based on their titles and summaries.

Rules:
- Assign 1-3 categories per article. Only assign categories where confidence >= 0.5.
- Use ONLY the category slugs provided. Do not invent categories.
- An article can belong to multiple categories (e.g., a tech regulation article could be "tech" and "politics").
- If no category fits with >= 0.5 confidence, assign an empty categories list.
- Respond using the classify_articles tool."""

CLASSIFICATION_TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        "articles": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "article_id": {"type": "string"},
                    "categories": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "slug": {"type": "string"},
                                "confidence": {"type": "number"},
                            },
                            "required": ["slug", "confidence"],
                        },
                    },
                },
                "required": ["article_id", "categories"],
            },
        }
    },
    "required": ["articles"],
}


def build_classification_prompt(
    articles: list[dict], categories: list[dict]
) -> str:
    cat_lines = []
    for c in categories:
        cat_lines.append(f"- {c['slug']}: {c['description']}")
    cats_text = "\n".join(cat_lines)

    article_lines = []
    for a in articles:
        line = f"[{a['id']}] {a['title']}"
        if a.get("summary"):
            line += f"\n    Summary: {a['summary'][:200]}"
        article_lines.append(line)
    articles_text = "\n\n".join(article_lines)

    return f"""CATEGORIES:
{cats_text}

ARTICLES TO CLASSIFY:

{articles_text}"""
