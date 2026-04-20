"""Tests for envoy.webhook."""
from __future__ import annotations

import json
import pytest
from unittest.mock import patch, MagicMock

from envoy.webhook import (
    WebhookError,
    register_webhook,
    remove_webhook,
    list_webhooks,
    dispatch_event,
)


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.webhook.get_store_dir", lambda: str(tmp_path))
    return str(tmp_path)


def test_register_webhook_persists(isolated_store):
    register_webhook("ci", "https://example.com/hook", ["push"], isolated_store)
    hooks = list_webhooks(isolated_store)
    assert len(hooks) == 1
    assert hooks[0]["name"] == "ci"
    assert hooks[0]["url"] == "https://example.com/hook"
    assert "push" in hooks[0]["events"]


def test_register_webhook_invalid_url_raises(isolated_store):
    with pytest.raises(WebhookError, match="Invalid URL"):
        register_webhook("bad", "ftp://nope", ["push"], isolated_store)


def test_remove_webhook_success(isolated_store):
    register_webhook("ci", "https://example.com/hook", ["push"], isolated_store)
    remove_webhook("ci", isolated_store)
    assert list_webhooks(isolated_store) == []


def test_remove_webhook_missing_raises(isolated_store):
    with pytest.raises(WebhookError, match="not found"):
        remove_webhook("ghost", isolated_store)


def test_list_webhooks_empty(isolated_store):
    assert list_webhooks(isolated_store) == []


def test_list_webhooks_multiple(isolated_store):
    register_webhook("a", "https://a.example.com", ["push"], isolated_store)
    register_webhook("b", "https://b.example.com", ["pull"], isolated_store)
    names = {h["name"] for h in list_webhooks(isolated_store)}
    assert names == {"a", "b"}


def test_dispatch_event_calls_matching_hooks(isolated_store):
    register_webhook("ci", "https://example.com/hook", ["push"], isolated_store)
    mock_resp = MagicMock()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_open:
        failed = dispatch_event("push", {"project": "myapp"}, isolated_store)
    assert failed == []
    mock_open.assert_called_once()


def test_dispatch_event_skips_non_matching_hooks(isolated_store):
    register_webhook("ci", "https://example.com/hook", ["pull"], isolated_store)
    with patch("urllib.request.urlopen") as mock_open:
        dispatch_event("push", {"project": "myapp"}, isolated_store)
    mock_open.assert_not_called()


def test_dispatch_event_returns_failed_on_error(isolated_store):
    import urllib.error
    register_webhook("ci", "https://example.com/hook", ["push"], isolated_store)
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        failed = dispatch_event("push", {"project": "myapp"}, isolated_store)
    assert "ci" in failed
