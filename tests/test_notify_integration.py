"""Integration tests: notify rules survive add/remove/list cycle."""
from __future__ import annotations

import pytest
from envoy.notify import add_rule, remove_rule, list_rules, dispatch, NotifyError


@pytest.fixture
def store(tmp_path):
    return tmp_path


def test_add_and_list_multiple_rules(store):
    add_rule("alpha", "push", "stdout", store_dir=store)
    add_rule("alpha", "pull", "stdout", store_dir=store)
    add_rule("beta", "rotate", "stdout", store_dir=store)
    all_rules = list_rules(store_dir=store)
    assert len(all_rules) == 3


def test_remove_leaves_others_intact(store):
    add_rule("proj", "push", "stdout", store_dir=store)
    add_rule("proj", "pull", "stdout", store_dir=store)
    remove_rule("proj", "push", store_dir=store)
    remaining = list_rules(store_dir=store)
    assert len(remaining) == 1
    assert remaining[0].event == "pull"


def test_dispatch_fires_only_matching_event(store, capsys):
    add_rule("proj", "push", "stdout", store_dir=store)
    add_rule("proj", "pull", "stdout", store_dir=store)
    result = dispatch("proj", "push", store_dir=store)
    assert len(result) == 1
    assert result[0] == "stdout"


def test_dispatch_multiple_rules_same_event(store, capsys):
    add_rule("proj", "push", "stdout", store_dir=store)
    add_rule("proj", "push", "stdout", store_dir=store)
    result = dispatch("proj", "push", store_dir=store)
    assert len(result) == 2


def test_no_rules_file_returns_empty_list(store):
    rules = list_rules(store_dir=store)
    assert rules == []


def test_remove_nonexistent_rule_raises(store):
    add_rule("proj", "push", "stdout", store_dir=store)
    with pytest.raises(NotifyError):
        remove_rule("proj", "rotate", store_dir=store)
