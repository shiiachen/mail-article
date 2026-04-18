from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from xml.etree import ElementTree

import requests

from zotero_digest.models import Paper

ARXIV_FEED_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivClient:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def fetch_recent(self, categories: list[str], lookback_hours: int, max_results: int) -> list[Paper]:
        query = _build_query(categories)
        response = self.session.get(
            ARXIV_FEED_URL,
            params={
                "search_query": query,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "start": 0,
                "max_results": max(max_results * 5, 50),
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        papers = _parse_feed(response.text)
        cutoff = datetime.now(UTC) - timedelta(hours=lookback_hours)
        return [paper for paper in papers if paper.published_at >= cutoff][: max(max_results * 3, max_results)]


def _build_query(categories: list[str]) -> str:
    if not categories:
        return "all:*"
    clauses = [f"cat:{category}" for category in categories]
    return " OR ".join(clauses)


def _parse_feed(xml_text: str) -> list[Paper]:
    root = ElementTree.fromstring(xml_text)
    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ATOM_NS):
        papers.append(_parse_entry(entry))
    return papers


def _parse_entry(entry: ElementTree.Element) -> Paper:
    paper_id = _text(entry, "atom:id").rstrip("/").split("/")[-1]
    links = entry.findall("atom:link", ATOM_NS)
    pdf_url = next((link.attrib.get("href", "") for link in links if link.attrib.get("title") == "pdf"), "")
    categories = [node.attrib.get("term", "") for node in entry.findall("atom:category", ATOM_NS) if node.attrib.get("term")]
    return Paper(
        paper_id=paper_id,
        title=" ".join(_text(entry, "atom:title").split()),
        abstract=" ".join(_text(entry, "atom:summary").split()),
        authors=[_text(author, "atom:name") for author in entry.findall("atom:author", ATOM_NS) if _text(author, "atom:name")],
        published_at=datetime.fromisoformat(_text(entry, "atom:published").replace("Z", "+00:00")),
        url=_text(entry, "atom:id"),
        pdf_url=pdf_url,
        categories=categories,
    )


def _text(node: ElementTree.Element, path: str) -> str:
    child = node.find(path, ATOM_NS)
    return child.text.strip() if child is not None and child.text else ""
