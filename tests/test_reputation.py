"""Tests for envoy.reputation."""

import json
import pytest

from envoy.storage import save_manifest
from envoy.reputation import (
    ReputationError,
    compute_reputation,
    get_reputation,
    list_reputations,
    remove_reputation,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.reputation.get_store_dir", lambda: tmp_path)
    save_manifest(tmp_path, {"alpha": "alpha.enc", "beta": "beta.enc"})
    return tmp_path


def test_compute_reputation_returns_record(isolated_store):
    rec = compute_reputation("alpha", store_dir=isolated_store)
    assert rec["project"] == "alpha"
    assert "score" in rec
    assert isinstance(rec["score"], int)


def test_compute_reputation_missing_project_raises(isolated_store):
    with pytest.raises(ReputationError, match="not found"):
        compute_reputation("ghost", store_dir=isolated_store)


def test_compute_reputation_zero_signals(isolated_store):
    rec = compute_reputation("alpha", store_dir=isolated_store, signals={})
    assert rec["score"] == 0


def test_compute_reputation_all_signals(isolated_store):
    signals = {
        "has_rating": True,
        "has_annotation": True,
        "has_metadata": True,
        "has_tags": True,
        "has_history": True,
        "has_audit": True,
        "has_snapshot": True,
    }
    rec = compute_reputation("alpha", store_dir=isolated_store, signals=signals)
    assert rec["score"] == 100


def test_compute_reputation_partial_signals(isolated_store):
    signals = {"has_rating": True, "has_history": True}
    rec = compute_reputation("alpha", store_dir=isolated_store, signals=signals)
    assert rec["score"] == 35


def test_get_reputation_missing_returns_none(isolated_store):
    assert get_reputation("alpha", store_dir=isolated_store) is None


def test_get_reputation_after_compute(isolated_store):
    compute_reputation("alpha", store_dir=isolated_store, signals={"has_tags": True})
    rec = get_reputation("alpha", store_dir=isolated_store)
    assert rec is not None
    assert rec["score"] == 10


def test_list_reputations_empty(isolated_store):
    assert list_reputations(store_dir=isolated_store) == []


def test_list_reputations_sorted_by_score(isolated_store):
    compute_reputation("alpha", store_dir=isolated_store, signals={"has_rating": True})
    compute_reputation("beta", store_dir=isolated_store, signals={"has_history": True, "has_snapshot": True})
    results = list_reputations(store_dir=isolated_store)
    assert results[0]["project"] == "beta"
    assert results[0]["score"] > results[1]["score"]


def test_remove_reputation_success(isolated_store):
    compute_reputation("alpha", store_dir=isolated_store)
    remove_reputation("alpha", store_dir=isolated_store)
    assert get_reputation("alpha", store_dir=isolated_store) is None


def test_remove_reputation_missing_raises(isolated_store):
    with pytest.raises(ReputationError, match="No reputation record"):
        remove_reputation("alpha", store_dir=isolated_store)
