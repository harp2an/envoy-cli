"""Integration tests: scorecard computed from real manifest data."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.scorecard import compute_score, get_scorecard, list_scorecards


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.scorecard.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    return tmp_path


def _write_manifest(store_dir: Path, data: dict) -> None:
    (store_dir / "manifest.json").write_text(json.dumps(data))


def test_score_increases_with_more_fields(isolated_store):
    _write_manifest(isolated_store, {
        "bare": {"file": "bare.enc"},
        "rich": {
            "file": "rich.enc",
            "description": "desc",
            "tags": ["x"],
            "annotation": "y",
            "rating": 4,
            "retention": 7,
        },
    })
    bare = compute_score("bare", store_dir=isolated_store)
    rich = compute_score("rich", store_dir=isolated_store)
    assert rich["score"] > bare["score"]


def test_scorecard_persists_across_calls(isolated_store):
    _write_manifest(isolated_store, {"proj": {"file": "proj.enc"}})
    compute_score("proj", store_dir=isolated_store)
    card = get_scorecard("proj", store_dir=isolated_store)
    assert card is not None
    assert card["score"] == 30


def test_recompute_updates_score(isolated_store):
    _write_manifest(isolated_store, {"proj": {"file": "proj.enc"}})
    compute_score("proj", store_dir=isolated_store)

    # Enrich manifest and recompute
    _write_manifest(isolated_store, {"proj": {"file": "proj.enc", "description": "new"}})
    result = compute_score("proj", store_dir=isolated_store)
    assert result["score"] == 50
    assert get_scorecard("proj", store_dir=isolated_store)["score"] == 50


def test_list_scorecards_sorted_by_score(isolated_store):
    _write_manifest(isolated_store, {
        "low": {"file": "l.enc"},
        "high": {"file": "h.enc", "description": "d", "tags": ["t"]},
    })
    compute_score("low", store_dir=isolated_store)
    compute_score("high", store_dir=isolated_store)
    cards = list_scorecards(store_dir=isolated_store)
    scores = [c["score"] for c in cards]
    assert len(scores) == 2
    assert set(scores) == {30, 65}
