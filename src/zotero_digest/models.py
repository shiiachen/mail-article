from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class ZoteroItem:
    key: str
    title: str
    abstract: str
    authors: list[str]
    tags: list[str]
    publication_title: str
    year: str

    @property
    def searchable_text(self) -> str:
        return " ".join(
            part
            for part in [
                self.title,
                self.abstract,
                " ".join(self.authors),
                " ".join(self.tags),
                self.publication_title,
                self.year,
            ]
            if part
        )


@dataclass(slots=True)
class Paper:
    paper_id: str
    title: str
    abstract: str
    authors: list[str]
    published_at: datetime
    url: str
    pdf_url: str
    categories: list[str]

    @property
    def searchable_text(self) -> str:
        return " ".join(
            part
            for part in [
                self.title,
                self.abstract,
                " ".join(self.authors),
                " ".join(self.categories),
            ]
            if part
        )


@dataclass(slots=True)
class MatchResult:
    paper: Paper
    matched_keywords: list[str]
    keyword_score: float
    similarity_score: float
    freshness_bonus: float
    final_score: float


@dataclass(slots=True)
class DigestResult:
    fetched_count: int
    matched_count: int
    sent_count: int
    matches: list[MatchResult] = field(default_factory=list)
