import pytest
from envoy.diff import parse_pairs, diff_envs, format_diff, diff_projects, DiffError
from envoy.storage import store_env
from envoy.crypto import encrypt
import os


def test_parse_simple_pairs():
    text = "FOO=bar\nBAZ=qux\n"
    assert parse_pairs(text) == {"FOO": "bar", "BAZ": "qux"}


def test_parse_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=1\n"
    assert parse_pairs(text) == {"FOO": "1"}


def test_parse_ignores_invalid_lines():
    text = "VALID=yes\nNOEQUALS\n"
    assert parse_pairs(text) == {"VALID": "yes"}


def test_diff_envs_added():
    result = diff_envs({}, {"NEW": "val"})
    assert result == [("added", "NEW", "", "val")]


def test_diff_envs_removed():
    result = diff_envs({"OLD": "val"}, {})
    assert result == [("removed", "OLD", "val", "")]


def test_diff_envs_changed():
    result = diff_envs({"K": "a"}, {"K": "b"})
    assert result == [("changed", "K", "a", "b")]


def test_diff_envs_unchanged():
    result = diff_envs({"K": "a"}, {"K": "a"})
    assert result == [("unchanged", "K", "a", "a")]


def test_format_diff_hides_unchanged_by_default():
    diff = [("unchanged", "K", "a", "a"), ("added", "NEW", "", "x")]
    out = format_diff(diff)
    assert "NEW" in out
    assert "unchanged" not in out
    assert " K=" not in out


def test_format_diff_shows_unchanged_when_requested():
    diff = [("unchanged", "K", "a", "a")]
    out = format_diff(diff, show_unchanged=True)
    assert "K=a" in out


def test_format_diff_changed_shows_arrow():
    diff = [("changed", "K", "old", "new")]
    out = format_diff(diff)
    assert "->" in out
    assert "old" in out
    assert "new" in out


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def test_diff_projects_roundtrip(isolated_store):
    pw = "secret"
    store_env("proj_a", encrypt("FOO=1\nBAR=2\n", pw), pw)
    store_env("proj_b", encrypt("FOO=1\nBAR=3\n", pw), pw)
    result = diff_projects("proj_a", pw, "proj_b", pw)
    statuses = {key: status for status, key, _, _ in result}
    assert statuses["FOO"] == "unchanged"
    assert statuses["BAR"] == "changed"


def test_diff_projects_missing_raises(isolated_store):
    with pytest.raises(DiffError, match="not found"):
        diff_projects("ghost", "pw", "ghost2", "pw")
