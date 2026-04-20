"""Tests for envoy.cmd_webhook."""
from __future__ import annotations

import sys
import pytest
from argparse import ArgumentParser, Namespace
from unittest.mock import patch

from envoy.cmd_webhook import (
    cmd_webhook_add,
    cmd_webhook_remove,
    cmd_webhook_list,
    register_webhook_parser,
)


def _args(**kwargs) -> Namespace:
    defaults = {"name": "ci", "url": "https://example.com", "events": "push,pull"}
    defaults.update(kwargs)
    return Namespace(**defaults)


def test_register_webhook_parser():
    p = ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_webhook_parser(sub)
    args = p.parse_args(["webhook", "add", "ci", "https://example.com"])
    assert args.name == "ci"
    assert args.url == "https://example.com"


def test_register_webhook_parser_list():
    p = ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_webhook_parser(sub)
    args = p.parse_args(["webhook", "list"])
    assert args.webhook_cmd == "list"


def test_cmd_webhook_add_success(capsys):
    with patch("envoy.cmd_webhook.register_webhook") as mock_reg:
        cmd_webhook_add(_args())
    mock_reg.assert_called_once_with("ci", "https://example.com", ["push", "pull"])
    out = capsys.readouterr().out
    assert "ci" in out


def test_cmd_webhook_add_error_exits(capsys):
    from envoy.webhook import WebhookError
    with patch("envoy.cmd_webhook.register_webhook", side_effect=WebhookError("bad url")):
        with pytest.raises(SystemExit):
            cmd_webhook_add(_args())
    assert "bad url" in capsys.readouterr().err


def test_cmd_webhook_remove_success(capsys):
    with patch("envoy.cmd_webhook.remove_webhook") as mock_rm:
        cmd_webhook_remove(_args())
    mock_rm.assert_called_once_with("ci")
    assert "removed" in capsys.readouterr().out


def test_cmd_webhook_remove_error_exits(capsys):
    from envoy.webhook import WebhookError
    with patch("envoy.cmd_webhook.remove_webhook", side_effect=WebhookError("not found")):
        with pytest.raises(SystemExit):
            cmd_webhook_remove(_args())


def test_cmd_webhook_list_empty(capsys):
    with patch("envoy.cmd_webhook.list_webhooks", return_value=[]):
        cmd_webhook_list(_args())
    assert "No webhooks" in capsys.readouterr().out


def test_cmd_webhook_list_with_entries(capsys):
    hooks = [{"name": "ci", "url": "https://example.com", "events": ["push"]}]
    with patch("envoy.cmd_webhook.list_webhooks", return_value=hooks):
        cmd_webhook_list(_args())
    out = capsys.readouterr().out
    assert "ci" in out
    assert "https://example.com" in out
