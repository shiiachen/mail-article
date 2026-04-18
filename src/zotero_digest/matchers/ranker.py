from __future__ import annotations

from collections import Counter

from zotero_digest.models import Paper, ZoteroItem
from zotero_digest.text import cosine_like_overlap, count_tokens


class ProfileRanker:
    def __init__(self, items: list[ZoteroItem]) -> None:
        texts = [item.searchable_text for item in items if item.searchable_text.strip()]
        counts = count_tokens(texts)
        total = sum(counts.values()) or 1
        self.profile_weights = {token: count / total for token, count in counts.items()}

    def score(self, paper: Paper) -> float:
        return cosine_like_overlap(self.profile_weights, paper.searchable_text)
