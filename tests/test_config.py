from __future__ import annotations

from zotero_digest.config import Config


def test_config_uses_defaults_for_empty_numeric_env(monkeypatch) -> None:
    values = {
        "ZOTERO_USER_ID": "user",
        "ZOTERO_API_KEY": "key",
        "ZOTERO_COLLECTION_KEY": "collection",
        "KEYWORDS": "machine learning",
        "SMTP_PORT": "",
        "MAX_RESULTS": "",
        "LOOKBACK_HOURS": "",
        "REQUEST_TIMEOUT": "",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    config = Config.from_env(require_email=False)

    assert config.smtp_port == 587
    assert config.max_results == 10
    assert config.lookback_hours == 24
    assert config.request_timeout == 30
