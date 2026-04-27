"""Tests for envoy.feedback module."""

import pytest

from envoy.feedback import (
    FeedbackError,
    add_feedback,
    clear_feedback,
    get_feedback,
    remove_feedback,
)
from envoy.storage import save_manifest, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.feedback.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.feedback.load_manifest", lambda d: _manifest(d))
    return tmp_path


def _manifest(store_dir):
    """Return a simple manifest with one project."""
    import json
    manifest_path = store_dir / "manifest.json"
    if manifest_path.exists():
        return json.loads(manifest_path.read_text())
    return {}


def _seed(store_dir, project="alpha"):
    import json
    manifest_path = store_dir / "manifest.json"
    data = {}
    if manifest_path.exists():
        data = json.loads(manifest_path.read_text())
    data[project] = f"{project}.env.enc"
    manifest_path.write_text(json.dumps(data))


def test_add_feedback_success(isolated_store):
    _seed(isolated_store)
    note = add_feedback("alpha", "looks good", store_dir=isolated_store)
    assert note == "looks good"


def test_add_feedback_persists(isolated_store):
    _seed(isolated_store)
    add_feedback("alpha", "first note", store_dir=isolated_store)
    add_feedback("alpha", "second note", store_dir=isolated_store)
    notes = get_feedback("alpha", store_dir=isolated_store)
    assert notes == ["first note", "second note"]


def test_get_feedback_empty_when_none(isolated_store):
    _seed(isolated_store)
    assert get_feedback("alpha", store_dir=isolated_store) == []


def test_add_feedback_missing_project_raises(isolated_store):
    with pytest.raises(FeedbackError, match="not found"):
        add_feedback("ghost", "hello", store_dir=isolated_store)


def test_add_feedback_empty_note_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(FeedbackError, match="empty"):
        add_feedback("alpha", "   ", store_dir=isolated_store)


def test_remove_feedback_success(isolated_store):
    _seed(isolated_store)
    add_feedback("alpha", "note one", store_dir=isolated_store)
    add_feedback("alpha", "note two", store_dir=isolated_store)
    removed = remove_feedback("alpha", 0, store_dir=isolated_store)
    assert removed == "note one"
    remaining = get_feedback("alpha", store_dir=isolated_store)
    assert remaining == ["note two"]


def test_remove_feedback_out_of_range_raises(isolated_store):
    _seed(isolated_store)
    add_feedback("alpha", "only note", store_dir=isolated_store)
    with pytest.raises(FeedbackError, match="out of range"):
        remove_feedback("alpha", 5, store_dir=isolated_store)


def test_remove_feedback_no_notes_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(FeedbackError, match="No feedback"):
        remove_feedback("alpha", 0, store_dir=isolated_store)


def test_clear_feedback_returns_count(isolated_store):
    _seed(isolated_store)
    add_feedback("alpha", "a", store_dir=isolated_store)
    add_feedback("alpha", "b", store_dir=isolated_store)
    count = clear_feedback("alpha", store_dir=isolated_store)
    assert count == 2
    assert get_feedback("alpha", store_dir=isolated_store) == []


def test_clear_feedback_empty_project(isolated_store):
    _seed(isolated_store)
    count = clear_feedback("alpha", store_dir=isolated_store)
    assert count == 0
