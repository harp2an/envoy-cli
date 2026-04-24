"""Tests for envoy.annotation."""

from __future__ import annotations

import pytest
from pathlib import Path

from envoy.storage import store_env, load_manifest
from envoy.annotation import (
    AnnotationError,
    set_annotation,
    get_annotation,
    remove_annotation,
    list_annotations,
)


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir: Path, project: str = "alpha") -> None:
    store_env(store_dir, project, b"KEY=val", "pass")


def test_set_annotation_persists(isolated_store):
    _seed(isolated_store)
    set_annotation(isolated_store, "alpha", "This is a note.")
    ann = get_annotation(isolated_store, "alpha")
    assert ann is not None
    assert ann["note"] == "This is a note."
    assert "updated_at" in ann


def test_get_annotation_missing_returns_none(isolated_store):
    _seed(isolated_store)
    assert get_annotation(isolated_store, "alpha") is None


def test_set_annotation_missing_project_raises(isolated_store):
    with pytest.raises(AnnotationError, match="not found"):
        set_annotation(isolated_store, "ghost", "note")


def test_set_annotation_empty_note_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(AnnotationError, match="empty"):
        set_annotation(isolated_store, "alpha", "   ")


def test_set_annotation_overwrites_existing(isolated_store):
    _seed(isolated_store)
    set_annotation(isolated_store, "alpha", "first")
    set_annotation(isolated_store, "alpha", "second")
    ann = get_annotation(isolated_store, "alpha")
    assert ann["note"] == "second"


def test_remove_annotation_success(isolated_store):
    _seed(isolated_store)
    set_annotation(isolated_store, "alpha", "to remove")
    remove_annotation(isolated_store, "alpha")
    assert get_annotation(isolated_store, "alpha") is None


def test_remove_annotation_missing_raises(isolated_store):
    _seed(isolated_store)
    with pytest.raises(AnnotationError, match="No annotation"):
        remove_annotation(isolated_store, "alpha")


def test_list_annotations_empty(isolated_store):
    assert list_annotations(isolated_store) == {}


def test_list_annotations_multiple(isolated_store):
    _seed(isolated_store, "alpha")
    _seed(isolated_store, "beta")
    set_annotation(isolated_store, "alpha", "note A")
    set_annotation(isolated_store, "beta", "note B")
    result = list_annotations(isolated_store)
    assert set(result.keys()) == {"alpha", "beta"}
    assert result["alpha"]["note"] == "note A"
    assert result["beta"]["note"] == "note B"
