from __future__ import annotations

from pathlib import Path

from zotero_digest.state import State, load_state, save_state


def test_state_round_trip(tmp_path: Path) -> None:
    path = tmp_path / "state.json"
    state = State(sent_ids={"a1", "b2"})

    save_state(path, state)
    loaded = load_state(path)

    assert loaded.sent_ids == {"a1", "b2"}
    assert loaded.last_run_at is not None
