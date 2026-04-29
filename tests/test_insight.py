"""Tests for envoy.insight module."""

import pytest

from envoy.storage import save_manifest
from envoy.insight import (
    InsightError,
    generate_insight,
    get_insight,
    list_insights,
    remove_insight,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.insight.get_store_dir", lambda: tmp_path)
    save_manifest(tmp_path, {"alpha": "alpha.enc", "beta": "beta.enc"})
    return tmp_path


def test_generate_insight_returns_record(isolated_store):
    record = generate_insight("alpha", {"has_lock": True, "has_tag": False}, isolated_store)
    assert record["project"] == "alpha"
    assert "score" in record
    assert "summary" in record
    assert record["score"] == 10


def test_generate_insight_persists(isolated_store):
    generate_insight("alpha", {"has_lock": True, "has_tag": True}, isolated_store)
    result = get_insight("alpha", isolated_store)
    assert result is not None
    assert result["score"] == 20


def test_generate_insight_missing_project_raises(isolated_store):
    with pytest.raises(InsightError, match="not found in manifest"):
        generate_insight("ghost", {"x": True}, isolated_store)


def test_generate_insight_empty_signals_raises(isolated_store):
    with pytest.raises(InsightError, match="must not be empty"):
        generate_insight("alpha", {}, isolated_store)


def test_get_insight_missing_returns_none(isolated_store):
    assert get_insight("alpha", isolated_store) is None


def test_list_insights_empty(isolated_store):
    assert list_insights(isolated_store) == []


def test_list_insights_multiple(isolated_store):
    generate_insight("alpha", {"a": True}, isolated_store)
    generate_insight("beta", {"b": True, "c": False}, isolated_store)
    results = list_insights(isolated_store)
    assert len(results) == 2
    projects = {r["project"] for r in results}
    assert projects == {"alpha", "beta"}


def test_remove_insight_success(isolated_store):
    generate_insight("alpha", {"x": True}, isolated_store)
    remove_insight("alpha", isolated_store)
    assert get_insight("alpha", isolated_store) is None


def test_remove_insight_missing_raises(isolated_store):
    with pytest.raises(InsightError, match="No insight found"):
        remove_insight("alpha", isolated_store)


def test_score_capped_at_100(isolated_store):
    signals = {f"s{i}": True for i in range(15)}
    record = generate_insight("alpha", signals, isolated_store)
    assert record["score"] == 100


def test_summary_includes_active_and_missing(isolated_store):
    record = generate_insight("alpha", {"lock": True, "tag": False}, isolated_store)
    assert "Active" in record["summary"]
    assert "Missing" in record["summary"]
