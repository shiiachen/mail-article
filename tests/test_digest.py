from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zotero_digest.digest import DigestBuilder
from zotero_digest.models import Paper, ZoteroItem
from zotero_digest.state import State


def _item(title: str, abstract: str) -> ZoteroItem:
    return ZoteroItem(
        key=title,
        title=title,
        abstract=abstract,
        authors=["Alice Example"],
        tags=["ml"],
        publication_title="Test Journal",
        year="2026",
    )


def _paper(paper_id: str, title: str, abstract: str) -> Paper:
    return Paper(
        paper_id=paper_id,
        title=title,
        abstract=abstract,
        authors=["Bob Researcher"],
        published_at=datetime.now(UTC) - timedelta(hours=2),
        url=f"https://arxiv.org/abs/{paper_id}",
        pdf_url=f"https://arxiv.org/pdf/{paper_id}.pdf",
        categories=["cs.LG"],
    )


def test_digest_filters_and_ranks_matches() -> None:
    builder = DigestBuilder(
        zotero_items=[
            _item("Graph neural networks for molecules", "representation learning for chemistry"),
            _item("Diffusion models in scientific discovery", "generative models for molecules"),
        ],
        keywords=["molecule", "diffusion"],
        max_results=5,
    )
    papers = [
        _paper("1", "Diffusion models for molecule design", "A molecule generation method"),
        _paper("2", "Unrelated database paper", "No overlap with configured keywords"),
    ]

    result = builder.build(papers, State())

    assert result.fetched_count == 2
    assert result.matched_count == 1
    assert result.sent_count == 1
    assert result.matches[0].paper.paper_id == "1"
    assert set(result.matches[0].matched_keywords) == {"molecule", "diffusion"}
    assert result.matches[0].final_score > 0


def test_digest_skips_previously_sent_papers() -> None:
    builder = DigestBuilder(
        zotero_items=[_item("Graph learning", "graph representations")],
        keywords=["graph"],
        max_results=5,
    )
    result = builder.build([_paper("seen", "Graph learning", "graph signals")], State(sent_ids={"seen"}))

    assert result.matched_count == 0
    assert result.sent_count == 0
