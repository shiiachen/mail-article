from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from zotero_digest.models import ZoteroItem


class ZoteroClient:
    def __init__(self, user_id: str, api_key: str, timeout: int = 30) -> None:
        self.user_id = user_id
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Zotero-API-Version": "3",
                "Zotero-API-Key": api_key,
            }
        )
        self.timeout = timeout

    def fetch_collection_items(self, collection_key: str) -> list[ZoteroItem]:
        url = f"https://api.zotero.org/users/{self.user_id}/collections/{collection_key}/items/top"
        start = 0
        items: list[ZoteroItem] = []
        while True:
            response = self.session.get(
                url,
                params={"format": "json", "limit": 100, "start": start},
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            if not payload:
                break
            items.extend(_to_zotero_item(entry) for entry in payload if _is_supported_item(entry.get("data", {})))
            if len(payload) < 100:
                break
            start += 100
        return items


def _is_supported_item(data: dict[str, Any]) -> bool:
    item_type = data.get("itemType", "")
    return item_type in {"journalArticle", "conferencePaper", "preprint", "report", "thesis"}


def _to_zotero_item(entry: dict[str, Any]) -> ZoteroItem:
    data = entry.get("data", {})
    creators = data.get("creators", [])
    tags = data.get("tags", [])
    return ZoteroItem(
        key=entry.get("key", ""),
        title=str(data.get("title", "")).strip(),
        abstract=str(data.get("abstractNote", "")).strip(),
        authors=[_creator_name(creator) for creator in creators if _creator_name(creator)],
        tags=[str(tag.get("tag", "")).strip() for tag in tags if str(tag.get("tag", "")).strip()],
        publication_title=str(data.get("publicationTitle", data.get("proceedingsTitle", ""))).strip(),
        year=_extract_year(data.get("date", "")),
    )


def _creator_name(creator: dict[str, Any]) -> str:
    first = str(creator.get("firstName", "")).strip()
    last = str(creator.get("lastName", "")).strip()
    name = str(creator.get("name", "")).strip()
    if name:
        return name
    return " ".join(part for part in [first, last] if part)


def _extract_year(raw: str) -> str:
    raw = str(raw).strip()
    if not raw:
        return ""
    try:
        return str(datetime.fromisoformat(raw[:10]).year)
    except ValueError:
        digits = "".join(ch for ch in raw if ch.isdigit())
        return digits[:4]
