import string

STOP_WORDS = frozenset({
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either", "neither",
    "this", "that", "these", "those", "it", "its", "with", "from", "by", "as",
    "into", "through", "about", "over", "after", "before", "between", "under",
    # News-specific stop words
    "says", "said", "report", "reports", "new", "just", "now", "breaking",
    "update", "latest", "today", "yesterday", "how", "why", "what", "who",
    "where", "when", "more", "than", "also", "very", "most",
})

_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def normalize_title(title: str) -> set[str]:
    tokens = title.lower().translate(_PUNCT_TABLE).split()
    return {t for t in tokens if t not in STOP_WORDS and len(t) > 1}


def jaccard_similarity(tokens_a: set[str], tokens_b: set[str]) -> float:
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)
