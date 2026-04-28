from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Config:
    zotero_user_id: str
    zotero_api_key: str
    zotero_collection_key: str
    keywords: list[str]
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    email_from: str
    email_to: list[str]
    arxiv_categories: list[str]
    max_results: int
    lookback_hours: int
    state_path: Path
    request_timeout: int

    @classmethod
    def from_env(cls, require_email: bool = True) -> "Config":
        raw_config = os.getenv("APP_CONFIG_JSON", "").strip()
        overlay = json.loads(raw_config) if raw_config else {}

        def get(name: str, default: str = "") -> str:
            return str(overlay.get(name.lower(), os.getenv(name, default))).strip()

        keywords = _parse_list(overlay.get("keywords", get("KEYWORDS")))
        recipients = _parse_list(overlay.get("email_to", get("EMAIL_TO")))
        categories = _parse_list(overlay.get("arxiv_categories", get("ARXIV_CATEGORIES")))

        config = cls(
            zotero_user_id=get("ZOTERO_USER_ID"),
            zotero_api_key=get("ZOTERO_API_KEY"),
            zotero_collection_key=get("ZOTERO_COLLECTION_KEY"),
            keywords=keywords,
            smtp_host=get("SMTP_HOST"),
            smtp_port=_parse_int(get("SMTP_PORT"), 587),
            smtp_user=get("SMTP_USER"),
            smtp_password=get("SMTP_PASSWORD"),
            email_from=get("EMAIL_FROM"),
            email_to=recipients,
            arxiv_categories=categories,
            max_results=_parse_int(get("MAX_RESULTS"), 10),
            lookback_hours=_parse_int(get("LOOKBACK_HOURS"), 24),
            state_path=Path(get("STATE_PATH", ".state/state.json")),
            request_timeout=_parse_int(get("REQUEST_TIMEOUT"), 30),
        )
        config.validate(require_email=require_email)
        return config

    def validate(self, require_email: bool = True) -> None:
        missing = [
            name
            for name, value in [
                ("ZOTERO_USER_ID", self.zotero_user_id),
                ("ZOTERO_API_KEY", self.zotero_api_key),
                ("ZOTERO_COLLECTION_KEY", self.zotero_collection_key),
            ]
            if not value
        ]
        if require_email:
            missing.extend(
                name
                for name, value in [
                    ("SMTP_HOST", self.smtp_host),
                    ("SMTP_USER", self.smtp_user),
                    ("SMTP_PASSWORD", self.smtp_password),
                    ("EMAIL_FROM", self.email_from),
                ]
                if not value
            )
        if not self.keywords:
            missing.append("KEYWORDS")
        if require_email and not self.email_to:
            missing.append("EMAIL_TO")
        if missing:
            joined = ", ".join(sorted(set(missing)))
            raise ValueError(f"Missing required configuration: {joined}")
        if self.max_results <= 0:
            raise ValueError("MAX_RESULTS must be greater than 0")
        if self.lookback_hours <= 0:
            raise ValueError("LOOKBACK_HOURS must be greater than 0")
        if self.smtp_port <= 0:
            raise ValueError("SMTP_PORT must be greater than 0")


def _parse_int(raw: object, default: int) -> int:
    value = str(raw or "").strip()
    return int(value) if value else default


def _parse_list(raw: object) -> list[str]:
    if isinstance(raw, list):
        values = raw
    else:
        values = str(raw or "").split(",")
    return [str(value).strip() for value in values if str(value).strip()]
