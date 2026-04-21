"""Tests for envoy.notify."""
from __future__ import annotations

import pytest
from pathlib import Path

from envoy.notify import (
    NotifyError,
    add_rule,
    remove_rule,
    list_rules,
    dispatch,
    VALID_EVENTS,
    VALID_CHANNELS,
)


@pytest.fixture
def isolated_store(tmp_path):
    return tmp_path


def test_add_rule_stdout(isolated_store):
    rule = add_rule("proj", "push", "stdout", store_dir=isolated_store)
    assert rule.project == "proj"
    assert rule.event == "push"
    assert rule.channel == "stdout"


def test_add_rule_persists(isolated_store):
    add_rule("proj", "pull", "stdout", store_dir=isolated_store)
    rules = list_rules(store_dir=isolated_store)
    assert len(rules) == 1
    assert rules[0].event == "pull"


def test_add_rule_webhook_valid_url(isolated_store):
    rule = add_rule("proj", "push", "webhook", target="https://example.com/hook", store_dir=isolated_store)
    assert rule.target == "https://example.com/hook"


def test_add_rule_webhook_invalid_url_raises(isolated_store):
    with pytest.raises(NotifyError, match="valid http"):
        add_rule("proj", "push", "webhook", target="not-a-url", store_dir=isolated_store)


def test_add_rule_unknown_event_raises(isolated_store):
    with pytest.raises(NotifyError, match="Unknown event"):
        add_rule("proj", "explode", "stdout", store_dir=isolated_store)


def test_add_rule_unknown_channel_raises(isolated_store):
    with pytest.raises(NotifyError, match="Unknown channel"):
        add_rule("proj", "push", "telegram", store_dir=isolated_store)


def test_remove_rule_success(isolated_store):
    add_rule("proj", "push", "stdout", store_dir=isolated_store)
    remove_rule("proj", "push", store_dir=isolated_store)
    assert list_rules(store_dir=isolated_store) == []


def test_remove_rule_missing_raises(isolated_store):
    with pytest.raises(NotifyError, match="No rule found"):
        remove_rule("proj", "push", store_dir=isolated_store)


def test_list_rules_filtered_by_project(isolated_store):
    add_rule("alpha", "push", "stdout", store_dir=isolated_store)
    add_rule("beta", "pull", "stdout", store_dir=isolated_store)
    rules = list_rules(project="alpha", store_dir=isolated_store)
    assert len(rules) == 1
    assert rules[0].project == "alpha"


def test_dispatch_stdout_returns_dispatched(isolated_store, capsys):
    add_rule("proj", "push", "stdout", store_dir=isolated_store)
    result = dispatch("proj", "push", {"key": "val"}, store_dir=isolated_store)
    assert result == ["stdout"]
    captured = capsys.readouterr()
    assert "proj" in captured.out
    assert "push" in captured.out


def test_dispatch_no_matching_rule_returns_empty(isolated_store):
    add_rule("proj", "push", "stdout", store_dir=isolated_store)
    result = dispatch("proj", "pull", {}, store_dir=isolated_store)
    assert result == []


def test_dispatch_wrong_project_returns_empty(isolated_store):
    add_rule("alpha", "push", "stdout", store_dir=isolated_store)
    result = dispatch("beta", "push", {}, store_dir=isolated_store)
    assert result == []
