from __future__ import annotations

import math
import re
from collections import Counter
from typing import Iterable

TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "into",
    "using",
    "via",
    "are",
    "was",
    "were",
    "been",
    "have",
    "has",
    "had",
    "into",
    "their",
    "than",
    "then",
    "they",
    "them",
    "our",
    "your",
    "about",
    "after",
    "before",
    "paper",
    "study",
    "based",
}


def tokenize(text: str) -> list[str]:
    tokens = [token for token in TOKEN_RE.findall(text.lower()) if token not in STOPWORDS]
    return tokens


def count_tokens(texts: Iterable[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))
    return counter


def cosine_like_overlap(profile_weights: dict[str, float], text: str) -> float:
    tokens = tokenize(text)
    if not tokens or not profile_weights:
        return 0.0
    counts = Counter(tokens)
    numerator = sum(profile_weights.get(token, 0.0) * count for token, count in counts.items())
    profile_norm = math.sqrt(sum(weight * weight for weight in profile_weights.values()))
    text_norm = math.sqrt(sum(count * count for count in counts.values()))
    if profile_norm == 0 or text_norm == 0:
        return 0.0
    return numerator / (profile_norm * text_norm)
