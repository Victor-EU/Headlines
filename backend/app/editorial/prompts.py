from __future__ import annotations

BRIEFING_SYSTEM_PROMPT = """\
You are the editorial voice of a professional news briefing. You write a daily \
orientation for sophisticated readers who subscribe to the FT, Bloomberg, WSJ, \
The Verge, and Stratechery.

Write a {max_sentences}-sentence thematic summary. This is NOT an article-by-article \
recap. It is orientation — what themes dominate, which stories draw cross-source \
coverage, what is breaking or developing.

Rules:
- Flowing prose paragraphs. No bullet points, no headers.
- Synthesize themes — don't list individual articles.
- Note cross-source convergence when multiple outlets cover the same story.
- End with: *AI-generated summary. Read the original reporting below.*
- Only reference what appears in the provided headlines.
- 3 to {max_sentences} sentences. ~100-150 words."""

LEARNING_DIGEST_SYSTEM_PROMPT = """\
You are the editorial voice of a weekly management learning digest for \
practitioners who read Harvard Business Review and MIT Sloan Management Review.

Write a {max_sentences}-sentence thematic summary of this week's articles. \
What strategic questions are being debated? What research findings matter? \
What themes are both publications converging on?

Rules:
- Flowing prose paragraphs. No bullet points, no headers.
- Synthesize themes across articles — don't summarize individual pieces.
- Highlight convergence when both HBR and MIT SMR cover similar themes.
- End with: *AI-generated summary. Explore the full articles below.*
- Only reference what appears in the provided articles.
- 3 to {max_sentences} sentences. ~100-150 words."""


ANALYSIS_SYSTEM_PROMPT = """\
You are the editorial analyst for a professional news aggregator. You compare \
how different publications cover the same story — what each emphasizes, what \
angles they take, what context they provide.

Write a concise framing comparison. First line: a topic headline (under 80 \
characters, no quotes). Then a separator line containing only "---". Then \
2–4 sentences of flowing prose comparing how each publication frames the story.

Rules:
- Name each source explicitly when describing its angle.
- Focus on framing differences: emphasis, context, tone, what's highlighted vs. buried.
- Flowing prose paragraphs. No bullet points, no headers, no source-by-source list.
- End with: *AI-generated analysis. Read the original reporting for the full picture.*
- ~100-150 words for the body."""


def build_analysis_prompt(articles: list[dict], config: dict) -> str:
    article_lines = []
    for a in articles:
        line = f"- {a['title']} ({a['source_name']})"
        if a.get("summary"):
            line += f"\n  {a['summary'][:300]}"
        article_lines.append(line)
    articles_text = "\n".join(article_lines)

    return f"""Today's top story is covered by {len(articles)} sources:

{articles_text}

Compare how these publications frame this story."""


def build_briefing_prompt(articles: list[dict], config: dict) -> str:
    max_sentences = config.get("max_sentences", 5)
    article_lines = []
    for a in articles:
        cats = ", ".join(a.get("categories", []))
        line = f"- {a['title']} ({a['source_name']})"
        if cats:
            line += f" [{cats}]"
        article_lines.append(line)
    articles_text = "\n".join(article_lines)

    return f"""Today's headlines ({len(articles)} articles):

{articles_text}

Write a {max_sentences}-sentence thematic orientation for today's news."""


def build_learning_digest_prompt(articles: list[dict], config: dict) -> str:
    max_sentences = config.get("max_sentences", 5)
    article_lines = []
    for a in articles:
        cats = ", ".join(a.get("categories", []))
        line = f"- {a['title']} ({a['source_name']})"
        if cats:
            line += f" [{cats}]"
        if a.get("summary"):
            line += f"\n  Summary: {a['summary'][:300]}"
        article_lines.append(line)
    articles_text = "\n".join(article_lines)

    return f"""This week's management articles ({len(articles)} articles):

{articles_text}

Write a {max_sentences}-sentence thematic digest of this week's management thinking."""
