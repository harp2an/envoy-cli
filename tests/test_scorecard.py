"""Unit tests for envoy.scorecard."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envoy.scorecard import (
    ScorecardError,
    compute_score,
    get_scorecard,
    list_scorecards,
    remove_scorecard,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.scorecard.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    return tmp_path


def _seed(store_dir: Path, project: str, extras: dict | None = None) -> None:
    manifest_path = store_dir / "manifest.json"
    entry = {"file": f"{project}.enc"}
    if extras:
        entry.update(extras)
    manifest = {}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
    manifest[project] = entry
    manifest_path.write_text(json.dumps(manifest))


def test_compute_score_minimal(isolated_store):
    _seed(isolated_store, "alpha")
    result = compute_score("alpha", store_dir=isolated_store)
    assert result["project"] == "alpha"
    assert result["score"] == 30  # only has_env_file
    assert result["checks"]["has_env_file"] is True
    assert result["checks"]["has_description"] is False


def test_compute_score_full(isolated_store):
    _seed(isolated_store, "beta", {
        "description": "A project",
        "tags": ["prod"],
        "annotation": "note",
        "rating": 5,
        "retention": 30,
    })
    result = compute_score("beta", store_dir=isolated_store)
    assert result["score"] == 100
    assert all(result["checks"].values())


def test_compute_score_missing_project_raises(isolated_store):
    _seed(isolated_store, "gamma")
    with pytest.raises(ScorecardError, match="not found"):
        compute_score("nope", store_dir=isolated_store)


def test_compute_score_persists(isolated_store):
    _seed(isolated_store, "delta")
    compute_score("delta", store_dir=isolated_store)
    card = get_scorecard("delta", store_dir=isolated_store)
    assert card is not None
    assert card["project"] == "delta"


def test_get_scorecard_missing_returns_none(isolated_store):
    assert get_scorecard("unknown", store_dir=isolated_store) is None


def test_list_scorecards_empty(isolated_store):
    assert list_scorecards(store_dir=isolated_store) == []


def test_list_scorecards_multiple(isolated_store):
    for name in ("p1", "p2"):
        _seed(isolated_store, name)
        compute_score(name, store_dir=isolated_store)
    cards = list_scorecards(store_dir=isolated_store)
    assert len(cards) == 2


def test_remove_scorecard_success(isolated_store):
    _seed(isolated_store, "epsilon")
    compute_score("epsilon", store_dir=isolated_store)
    remove_scorecard("epsilon", store_dir=isolated_store)
    assert get_scorecard("epsilon", store_dir=isolated_store) is None


def test_remove_scorecard_missing_raises(isolated_store):
    with pytest.raises(ScorecardError, match="No scorecard"):
        remove_scorecard("ghost", store_dir=isolated_store)
