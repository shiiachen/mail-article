from __future__ import annotations

from datetime import UTC, datetime

from zotero_digest.matchers.keywords import match_keywords
from zotero_digest.matchers.ranker import ProfileRanker
from zotero_digest.models import DigestResult, MatchResult, Paper, ZoteroItem
from zotero_digest.state import State


class DigestBuilder:
    def __init__(self, zotero_items: list[ZoteroItem], keywords: list[str], max_results: int) -> None:
        self.keywords = keywords
        self.max_results = max_results
        self.ranker = ProfileRanker(zotero_items)

    def build(self, papers: list[Paper], state: State) -> DigestResult:
        matches: list[MatchResult] = []
        now = datetime.now(UTC)
        for paper in papers:
            if paper.paper_id in state.sent_ids:
                continue
            matched_keywords, keyword_score = match_keywords(paper, self.keywords)
            if not matched_keywords:
                continue
            similarity_score = self.ranker.score(paper)
            age_hours = max((now - paper.published_at).total_seconds() / 3600, 0)
            freshness_bonus = max(0.0, 1.0 - age_hours / 48)
            final_score = keyword_score + similarity_score + freshness_bonus
            matches.append(
                MatchResult(
                    paper=paper,
                    matched_keywords=matched_keywords,
                    keyword_score=keyword_score,
                    similarity_score=similarity_score,
                    freshness_bonus=freshness_bonus,
                    final_score=final_score,
                )
            )
        matches.sort(key=lambda item: item.final_score, reverse=True)
        selected = matches[: self.max_results]
        return DigestResult(
            fetched_count=len(papers),
            matched_count=len(matches),
            sent_count=len(selected),
            matches=selected,
        )

    @staticmethod
    def mark_sent(result: DigestResult, state: State) -> None:
        for match in result.matches:
            state.sent_ids.add(match.paper.paper_id)
        state.last_run_at = datetime.now(UTC)
