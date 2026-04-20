"""Quota management: enforce per-project size and key-count limits."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envoy.storage import get_store_dir, load_manifest

DEFAULT_MAX_KEYS = 200
DEFAULT_MAX_BYTES = 1024 * 512  # 512 KB


class QuotaError(Exception):
    """Raised when a quota limit is exceeded or configuration is invalid."""


def _quota_path(store_dir: Optional[Path] = None) -> Path:
    return (store_dir or get_store_dir()) / "quotas.json"


def _load_quotas(store_dir: Optional[Path] = None) -> Dict[str, dict]:
    path = _quota_path(store_dir)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def _save_quotas(quotas: Dict[str, dict], store_dir: Optional[Path] = None) -> None:
    _quota_path(store_dir).write_text(json.dumps(quotas, indent=2))


def set_quota(
    project: str,
    max_keys: Optional[int] = None,
    max_bytes: Optional[int] = None,
    store_dir: Optional[Path] = None,
) -> None:
    """Set quota limits for a project."""
    manifest = load_manifest(store_dir)
    if project not in manifest:
        raise QuotaError(f"Project '{project}' not found")
    if max_keys is not None and max_keys < 1:
        raise QuotaError("max_keys must be >= 1")
    if max_bytes is not None and max_bytes < 1:
        raise QuotaError("max_bytes must be >= 1")
    quotas = _load_quotas(store_dir)
    quotas[project] = {
        "max_keys": max_keys if max_keys is not None else DEFAULT_MAX_KEYS,
        "max_bytes": max_bytes if max_bytes is not None else DEFAULT_MAX_BYTES,
    }
    _save_quotas(quotas, store_dir)


def get_quota(project: str, store_dir: Optional[Path] = None) -> dict:
    """Return quota config for a project (defaults if not set)."""
    quotas = _load_quotas(store_dir)
    return quotas.get(project, {"max_keys": DEFAULT_MAX_KEYS, "max_bytes": DEFAULT_MAX_BYTES})


def remove_quota(project: str, store_dir: Optional[Path] = None) -> None:
    """Remove custom quota for a project (reverts to defaults)."""
    quotas = _load_quotas(store_dir)
    if project not in quotas:
        raise QuotaError(f"No custom quota set for project '{project}'")
    del quotas[project]
    _save_quotas(quotas, store_dir)


def check_quota(
    project: str,
    content: str,
    store_dir: Optional[Path] = None,
) -> None:
    """Raise QuotaError if content exceeds the project quota."""
    quota = get_quota(project, store_dir)
    byte_size = len(content.encode())
    if byte_size > quota["max_bytes"]:
        raise QuotaError(
            f"Content size {byte_size} bytes exceeds max_bytes={quota['max_bytes']} for '{project}'"
        )
    key_count = sum(
        1
        for line in content.splitlines()
        if line.strip() and not line.strip().startswith("#") and "=" in line
    )
    if key_count > quota["max_keys"]:
        raise QuotaError(
            f"Key count {key_count} exceeds max_keys={quota['max_keys']} for '{project}'"
        )
