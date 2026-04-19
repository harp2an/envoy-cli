"""Shared access tokens for exporting env references to other users."""

import secrets
import json
from pathlib import Path
from typing import Optional
from envoy.storage import get_store_dir

SHARE_FILE = "shares.json"


class ShareError(Exception):
    pass


def _share_path() -> Path:
    return get_store_dir() / SHARE_FILE


def _load_shares() -> dict:
    p = _share_path()
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_shares(shares: dict) -> None:
    _share_path().write_text(json.dumps(shares, indent=2))


def create_share(project: str, note: str = "") -> str:
    """Generate a share token for a project and persist it."""
    shares = _load_shares()
    token = secrets.token_urlsafe(24)
    shares[token] = {"project": project, "note": note}
    _save_shares(shares)
    return token


def revoke_share(token: str) -> None:
    """Remove a share token."""
    shares = _load_shares()
    if token not in shares:
        raise ShareError(f"Token not found: {token}")
    del shares[token]
    _save_shares(shares)


def resolve_share(token: str) -> Optional[dict]:
    """Return share metadata or None if token is unknown."""
    return _load_shares().get(token)


def list_shares() -> list:
    """Return all active shares as a list of dicts."""
    shares = _load_shares()
    return [{"token": t, **meta} for t, meta in shares.items()]
