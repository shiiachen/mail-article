from __future__ import annotations

from collections import Counter

from zotero_digest.models import Paper


def match_keywords(paper: Paper, keywords: list[str]) -> tuple[list[str], float]:
    lowered = paper.searchable_text.lower()
    matched: list[str] = []
    weighted_hits: Counter[str] = Counter()

    title = paper.title.lower()
    abstract = paper.abstract.lower()
    authors = " ".join(paper.authors).lower()
    categories = " ".join(paper.categories).lower()

    for keyword in keywords:
        term = keyword.strip().lower()
        if not term or term not in lowered:
            continue
        matched.append(keyword)
        score = 1.0
        if term in title:
            score += 2.0
        if term in abstract:
            score += 1.0
        if term in authors or term in categories:
            score += 0.5
        weighted_hits[keyword] += score

    return matched, float(sum(weighted_hits.values()))
