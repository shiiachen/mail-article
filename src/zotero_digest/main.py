from __future__ import annotations

import argparse
import json

from zotero_digest.config import Config
from zotero_digest.digest import DigestBuilder
from zotero_digest.emailer import build_email, send_email
from zotero_digest.sources.arxiv_client import ArxivClient
from zotero_digest.state import load_state, save_state
from zotero_digest.zotero_client import ZoteroClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a daily paper digest from Zotero interests and keywords")
    parser.add_argument("--dry-run", action="store_true", help="Print the digest instead of sending email")
    args = parser.parse_args()

    config = Config.from_env(require_email=not args.dry_run)
    state = load_state(config.state_path)

    zotero_client = ZoteroClient(config.zotero_user_id, config.zotero_api_key, timeout=config.request_timeout)
    zotero_items = zotero_client.fetch_collection_items(config.zotero_collection_key)

    arxiv_client = ArxivClient(timeout=config.request_timeout)
    papers = arxiv_client.fetch_recent(config.arxiv_categories, config.lookback_hours, config.max_results)

    digest = DigestBuilder(zotero_items, config.keywords, config.max_results).build(papers, state)

    if args.dry_run:
        payload = {
            "fetched_count": digest.fetched_count,
            "matched_count": digest.matched_count,
            "sent_count": digest.sent_count,
            "matches": [
                {
                    "paper_id": match.paper.paper_id,
                    "title": match.paper.title,
                    "matched_keywords": match.matched_keywords,
                    "final_score": round(match.final_score, 4),
                    "url": match.paper.url,
                }
                for match in digest.matches
            ],
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    message = build_email(digest.matches, digest.fetched_count, config.email_from, config.email_to)
    send_email(message, config.smtp_host, config.smtp_port, config.smtp_user, config.smtp_password)
    DigestBuilder.mark_sent(digest, state)
    save_state(config.state_path, state)


if __name__ == "__main__":
    main()
