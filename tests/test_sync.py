"""Tests for envoy.sync module."""

import json
from io import BytesIO
from unittest.mock import patch, MagicMock

import pytest

from envoy.sync import push_env, pull_env, list_remote_projects, SyncError


REMOTE = "http://localhost:8000"
PROJECT = "myapp"
PASSWORD = "s3cr3t"
PLAINTEXT = "DB_URL=postgres://localhost/myapp\nDEBUG=true"


def _make_response(status: int, body: dict):
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.read.return_value = json.dumps(body).encode()
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_push_env_no_remote_raises():
    with patch("envoy.sync.DEFAULT_REMOTE_URL", ""):
        with patch("envoy.sync.load_env", return_value=PLAINTEXT):
            with pytest.raises(SyncError, match="No remote URL"):
                push_env(PROJECT, PASSWORD, remote_url=None)


def test_push_env_success():
    mock_resp = _make_response(200, {})
    with patch("envoy.sync.load_env", return_value=PLAINTEXT):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = push_env(PROJECT, PASSWORD, remote_url=REMOTE)
    assert result == f"{REMOTE}/envs/{PROJECT}"


def test_push_env_bad_status_raises():
    mock_resp = _make_response(500, {})
    with patch("envoy.sync.load_env", return_value=PLAINTEXT):
        with patch("urllib.request.urlopen", return_value=mock_resp):
            with pytest.raises(SyncError, match="status 500"):
                push_env(PROJECT, PASSWORD, remote_url=REMOTE)


def test_pull_env_success():
    from envoy.crypto import encrypt
    ciphertext = encrypt(PLAINTEXT, PASSWORD)
    mock_resp = _make_response(200, {"data": ciphertext})
    with patch("urllib.request.urlopen", return_value=mock_resp):
        with patch("envoy.sync.store_env") as mock_store:
            pull_env(PROJECT, PASSWORD, remote_url=REMOTE)
            mock_store.assert_called_once_with(PROJECT, PLAINTEXT, PASSWORD)


def test_pull_env_missing_data_raises():
    mock_resp = _make_response(200, {})
    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(SyncError, match="missing 'data'"):
            pull_env(PROJECT, PASSWORD, remote_url=REMOTE)


def test_list_remote_projects():
    mock_resp = _make_response(200, {"projects": ["app1", "app2"]})
    with patch("urllib.request.urlopen", return_value=mock_resp):
        projects = list_remote_projects(remote_url=REMOTE)
    assert projects == ["app1", "app2"]


def test_list_remote_no_url_raises():
    with patch("envoy.sync.DEFAULT_REMOTE_URL", ""):
        with pytest.raises(SyncError, match="No remote URL"):
            list_remote_projects(remote_url=None)
