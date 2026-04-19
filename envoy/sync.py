"""Remote sync module for envoy-cli."""

import json
import os
import urllib.request
import urllib.error
from typing import Optional

from envoy.crypto import encrypt, decrypt
from envoy.storage import load_env, store_env, load_manifest


DEFAULT_REMOTE_URL = os.environ.get("ENVOY_REMOTE_URL", "")


class SyncError(Exception):
    pass


def _build_url(remote_url: Optional[str], path: str) -> str:
    """Resolve the remote URL and append a path segment."""
    url = remote_url or DEFAULT_REMOTE_URL
    if not url:
        raise SyncError("No remote URL configured. Set ENVOY_REMOTE_URL or pass --remote.")
    return f"{url.rstrip('/')}/{path.lstrip('/')}"


def push_env(project: str, password: str, remote_url: Optional[str] = None) -> str:
    """Encrypt and push an env to the remote store. Returns remote URL."""
    endpoint = _build_url(remote_url, f"/envs/{project}")

    plaintext = load_env(project, password)
    ciphertext = encrypt(plaintext, password)

    payload = json.dumps({"project": project, "data": ciphertext}).encode()
    req = urllib.request.Request(
        endpoint,
        data=payload,
        method="PUT",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status not in (200, 201, 204):
                raise SyncError(f"Remote returned status {resp.status}")
    except urllib.error.URLError as exc:
        raise SyncError(f"Failed to push env: {exc}") from exc

    return endpoint


def pull_env(project: str, password: str, remote_url: Optional[str] = None) -> None:
    """Pull and decrypt an env from the remote store, saving it locally."""
    endpoint = _build_url(remote_url, f"/envs/{project}")

    req = urllib.request.Request(endpoint, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise SyncError(f"Failed to pull env: {exc}") from exc

    ciphertext = body.get("data")
    if not ciphertext:
        raise SyncError("Remote response missing 'data' field.")

    plaintext = decrypt(ciphertext, password)
    store_env(project, plaintext, password)


def list_remote_projects(remote_url: Optional[str] = None) -> list:
    """List projects available on the remote store."""
    endpoint = _build_url(remote_url, "/envs")

    req = urllib.request.Request(endpoint, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.URLError as exc:
        raise SyncError(f"Failed to list remote projects: {exc}") from exc

    return body.get("projects", [])
