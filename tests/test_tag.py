"""Tests for envoy.tag."""

import pytest
from unittest.mock import patch

from envoy.tag import TagError, add_tag, remove_tag, list_tags, find_by_tag


BASE_MANIFEST = {
    "alpha": {"file": "alpha.enc", "tags": ["prod"]},
    "beta": {"file": "beta.enc"},
}


def _manifest():
    import copy
    return copy.deepcopy(BASE_MANIFEST)


def test_add_tag_success():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m), \
         patch("envoy.tag.save_manifest") as sv:
        add_tag("beta", "staging")
        assert "staging" in m["beta"]["tags"]
        sv.assert_called_once_with(m)


def test_add_tag_duplicate_raises():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m), \
         patch("envoy.tag.save_manifest"):
        with pytest.raises(TagError, match="already exists"):
            add_tag("alpha", "prod")


def test_add_tag_missing_project_raises():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m):
        with pytest.raises(TagError, match="not found"):
            add_tag("ghost", "x")


def test_remove_tag_success():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m), \
         patch("envoy.tag.save_manifest") as sv:
        remove_tag("alpha", "prod")
        assert "prod" not in m["alpha"]["tags"]
        sv.assert_called_once()


def test_remove_tag_missing_raises():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m), \
         patch("envoy.tag.save_manifest"):
        with pytest.raises(TagError, match="not found"):
            remove_tag("alpha", "nope")


def test_list_tags_returns_tags():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m):
        assert list_tags("alpha") == ["prod"]


def test_list_tags_empty():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m):
        assert list_tags("beta") == []


def test_find_by_tag():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m):
        result = find_by_tag("prod")
        assert result == ["alpha"]


def test_find_by_tag_none():
    m = _manifest()
    with patch("envoy.tag.load_manifest", return_value=m):
        assert find_by_tag("unknown") == []
