from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(slots=True)
class State:
    sent_ids: set[str] = field(default_factory=set)
    last_run_at: datetime | None = None


def load_state(path: Path) -> State:
    if not path.exists():
        return State()
    data = json.loads(path.read_text())
    last_run_at = data.get("last_run_at")
    return State(
        sent_ids=set(data.get("sent_ids", [])),
        last_run_at=datetime.fromisoformat(last_run_at) if last_run_at else None,
    )


def save_state(path: Path, state: State) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "sent_ids": sorted(state.sent_ids),
        "last_run_at": (state.last_run_at or datetime.now(UTC)).isoformat(),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
