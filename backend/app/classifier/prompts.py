from __future__ import annotations

CLASSIFICATION_SYSTEM_PROMPT = """You are a news article classifier. You assign articles to categories and rate their interest level for high-agency decision-makers.

Rules:
- Assign 1-3 categories per article. Only assign categories where confidence >= 0.5.
- Use ONLY the category slugs provided. Do not invent categories.
- An article can belong to multiple categories (e.g., a tech regulation article could be "tech" and "politics").
- If no category fits with >= 0.5 confidence, assign an empty categories list.
- Rate each article's interest_score from 1-5 for a busy executive or investor:
  5 = Must Read: structural shift, market-moving event, changes how you think about an industry
  4 = High Signal: significant development with clear implications for decisions
  3 = Worth Knowing: solid reporting on a meaningful topic, doesn't change decisions today
  2 = Background: incremental update, routine coverage, narrow interest
  1 = Skip: listicles, PR rewrites, trivial updates, re-coverage with no new information
  Most articles should score 2-3. Reserve 4-5 for genuinely significant developments.
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
                    "interest_score": {
                        "type": "integer",
                        "description": "1-5 interest rating for high-agency decision-makers",
                    },
                },
                "required": ["article_id", "categories", "interest_score"],
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
